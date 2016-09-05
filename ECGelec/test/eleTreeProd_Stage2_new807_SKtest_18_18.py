import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
from Configuration.StandardSequences.Eras import eras
import os
import sys
import commands

options = VarParsing.VarParsing ('analysis')



from Configuration.StandardSequences.Eras import eras

process = cms.Process('RAW2DIGI',eras.Run2_2016)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2016Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')


process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100)
)

options.parseArguments()

# Input source
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring('root://eoscms.cern.ch//eos/cms/store/data/Run2016B/DoubleEG/RAW-RECO/ZElectron-PromptReco-v2/000/273/730/00000/0E51CDAD-4E21-E611-BF6A-02163E01459C.root'),
                            #fileNames = cms.untracked.vstring(options.inputFiles),
                            #secondaryFileNames = cms.untracked.vstring()
)


import FWCore.PythonUtilities.LumiList as LumiList
#process.source.lumisToProcess = LumiList.LumiList(filename = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-274421_13TeV_PromptReco_Collisions16_JSON.txt').getVLuminosityBlockRange()


# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('l1NtupleRECO nevts:200'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
#process.GlobalTag.globaltag = '80X_dataRun2_Prompt_v8'
process.GlobalTag.globaltag = '80X_dataRun2_Prompt_ICHEP16JEC_v0'
process.GlobalTag.toGet = cms.VPSet( #sFGVB thresholds.
           cms.PSet(record = cms.string("EcalTPGFineGrainStripEERcd"),
                     tag = cms.string("EcalTPGFineGrainStrip_18"),
                     connect =cms.string('frontier://FrontierPrep/CMS_CONDITIONS')
                    ),
            cms.PSet(record = cms.string("EcalTPGSpikeRcd"),
                     tag = cms.string("EcalTPGSpike_18"),
                     connect =cms.string('frontier://FrontierPrep/CMS_CONDITIONS')
                    )
            )

#process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_data', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.endjob_step = cms.EndPath(process.endOfProcess)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.endjob_step)

# customisation of the process.

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseReEmul
from L1Trigger.Configuration.customiseReEmul import L1TReEmulFromRAWsimEcalTP

#call to customisation function L1TReEmulFromRAW imported from L1Trigger.Configuration.customiseReEmul
process = L1TReEmulFromRAWsimEcalTP(process)



# Automatic addition of the customisation function from L1Trigger.L1TNtuples.customiseL1Ntuple
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleEMU 

#call to customisation function L1NtupleAODEMU imported from L1Trigger.L1TNtuples.customiseL1Ntuple
process = L1NtupleEMU(process)


# Automatic addition of the customisation function from L1Trigger.Configuration.customiseSettings
from L1Trigger.Configuration.customiseSettings import L1TSettingsToCaloStage2Params_v2_0

#call to customisation function L1TSettingsToCaloStage2Params_v2_0 imported from L1Trigger.Configuration.customiseSettings
process = L1TSettingsToCaloStage2Params_v2_0(process)

# Automatic addition of the customisation function from L1Trigger.Configuration.customiseUtils
from L1Trigger.Configuration.customiseUtils import L1TTurnOffUnpackStage2GtGmtAndCalo 

#call to customisation function L1TTurnOffUnpackStage2GtGmtAndCalo imported from L1Trigger.Configuration.customiseUtils
process = L1TTurnOffUnpackStage2GtGmtAndCalo(process)

# End of customisation functions



from EventFilter.L1TRawToDigi.caloStage2Digis_cfi import caloStage2Digis
process.rawCaloStage2Digis = caloStage2Digis.clone()
process.rawCaloStage2Digis.InputLabel = cms.InputTag('rawDataCollector')


# ---------------------------------------------------------------------
# JETS
# ---------------------------------------------------------------------
# JPT
process.load('RecoJets.Configuration.RecoPFJets_cff')


# ---------------------------------------------------------------------
# Fast Jet Rho Correction
# ---------------------------------------------------------------------
process.load('RecoJets.JetProducers.kt4PFJets_cfi')
process.kt6PFJets = process.kt4PFJets.clone( rParam = 0.6, doRhoFastjet = True )
process.kt6PFJets.Rho_EtaMax = cms.double(2.5)


# ---------------------------------------------------------------------
# Vertexing DA
# ---------------------------------------------------------------------
from RecoVertex.Configuration.RecoVertex_cff import *



# ---------------------------------------------------------------------
# Set up electron ID (VID framework)
# ---------------------------------------------------------------------
from PhysicsTools.SelectorUtils.tools.vid_id_tools import *
# turn on VID producer, indicate data format  to be
# DataFormat.AOD or DataFormat.MiniAOD, as appropriate 
dataFormat = DataFormat.AOD
switchOnVIDElectronIdProducer(process, dataFormat)
process.load("RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cfi")
process.egmGsfElectronIDSequence = cms.Sequence(process.egmGsfElectronIDs)
# define which IDs we want to produce
my_id_modules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Spring15_50ns_V2_cff',
                 'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Spring15_25ns_V1_cff']
#add them to the VID producer
for idmod in my_id_modules:
    setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)




# ---------------------------------------------------------------------
# Unpack Ecal Digis
# ---------------------------------------------------------------------
process.load("EventFilter.EcalRawToDigi.EcalUnpackerMapping_cfi");
process.load("EventFilter.EcalRawToDigi.EcalUnpackerData_cfi");
#process.ecalEBunpacker.InputLabel = cms.InputTag('rawDataCollector');

# ---------------------------------------------------------------------
# Simulate Ecal Trigger Primitives
# ---------------------------------------------------------------------

# Config from file
#process.load('SimCalorimetry.EcalTrigPrimProducers.ecalTrigPrimESProducer_cff')
 
# take EBDigis from saved RAW-RECO collection
#process.load("SimCalorimetry.EcalTrigPrimProducers.ecalTriggerPrimitiveDigis_cff")
#process.simEcalTriggerPrimitiveDigis.Label = 'ecalEBunpacker'
process.simEcalTriggerPrimitiveDigis.Label = 'ecalDigis'
process.simEcalTriggerPrimitiveDigis.InstanceEB =  'ebDigis'
process.simEcalTriggerPrimitiveDigis.InstanceEE =  'eeDigis'
process.simEcalTriggerPrimitiveDigis.BarrelOnly =False 


process.load('Configuration.StandardSequences.SimL1Emulator_cff') 
process.load('L1Trigger.Configuration.L1Trigger_EventContent_cff')

# emulator trigger
#process.simRctDigis.ecalDigis = cms.VInputTag(cms.InputTag("simEcalTriggerPrimitiveDigis"))
#process.simRctDigis.hcalDigis = cms.VInputTag(cms.InputTag("hcalDigis"))
#process.simGctDigis.inputLabel = cms.InputTag("simRctDigis")



#Stage 1 update
#process.caloStage1FinalDigis = cms.EDProducer(
#    "L1TPhysicalEtAdder",
#    InputCollection = cms.InputTag("caloStage1Digis"),
#    InputRlxTauCollection = cms.InputTag("caloStage1Digis:rlxTaus"),
#    InputIsoTauCollection = cms.InputTag("caloStage1Digis:isoTaus"),
#    ## InputPreGtJetCollection = cms.InputTag("caloStage1Digis:preGtJets"),
#    InputPreGtJetCollection = cms.InputTag("caloStage1Digis"),
#    InputHFSumsCollection = cms.InputTag("caloStage1Digis:HFRingSums"),
#    InputHFCountsCollection = cms.InputTag("caloStage1Digis:HFBitCounts")
#    )
#process.load("L1Trigger.L1TCommon.caloStage1LegacyFormatDigis_cfi")





# L1 extra for the re-simulated candidates
#process.l1extraParticles = cms.EDProducer("L1ExtraParticlesProd",
#                                          muonSource = cms.InputTag("gtDigis"),
#                                          etTotalSource = cms.InputTag("simGctDigis"),
#                                          nonIsolatedEmSource = cms.InputTag("simGctDigis","nonIsoEm"),
#                                          etMissSource = cms.InputTag("simGctDigis"),
#                                          htMissSource = cms.InputTag("simGctDigis"),
#                                          produceMuonParticles = cms.bool(False),
#                                          forwardJetSource = cms.InputTag("simGctDigis","forJets"),
#                                          centralJetSource = cms.InputTag("simGctDigis","cenJets"),
#                                          produceCaloParticles = cms.bool(True),
#                                          tauJetSource = cms.InputTag("simGctDigis","tauJets"),
#                                          isoTauJetSource = cms.InputTag("simGctDigis","isoTauJets"),
#                                          isolatedEmSource = cms.InputTag("simGctDigis","isoEm"),
#                                          etHadSource = cms.InputTag("simGctDigis"),
#                                          hfRingEtSumsSource = cms.InputTag("simGctDigis"),
#                                          hfRingBitCountsSource = cms.InputTag("simGctDigis"),
#                                          centralBxOnly = cms.bool(True),
#                                          ignoreHtMiss = cms.bool(False)
#                                          )


# L1 extra for the online candidates
process.l1extraParticlesOnline = cms.EDProducer("L1ExtraParticlesProd",
                                                muonSource = cms.InputTag("gtDigis"),
                                                etTotalSource = cms.InputTag("caloStage1LegacyFormatDigis"),
                                                nonIsolatedEmSource = cms.InputTag("caloStage1LegacyFormatDigis","nonIsoEm"),
                                                etMissSource = cms.InputTag("caloStage1LegacyFormatDigis"),
                                                htMissSource = cms.InputTag("caloStage1LegacyFormatDigis"),
                                                produceMuonParticles = cms.bool(False),
                                                forwardJetSource = cms.InputTag("caloStage1LegacyFormatDigis","forJets"),
                                                centralJetSource = cms.InputTag("caloStage1LegacyFormatDigis","cenJets"),
                                                produceCaloParticles = cms.bool(True),
                                                tauJetSource = cms.InputTag("caloStage1LegacyFormatDigis","tauJets"),
                                                isoTauJetSource = cms.InputTag("caloStage1LegacyFormatDigis","isoTauJets"),
                                                isolatedEmSource = cms.InputTag("caloStage1LegacyFormatDigis","isoEm"),
                                                etHadSource = cms.InputTag("caloStage1LegacyFormatDigis"),
                                                hfRingEtSumsSource = cms.InputTag("caloStage1LegacyFormatDigis"),
                                                hfRingBitCountsSource = cms.InputTag("caloStage1LegacyFormatDigis"),
                                                centralBxOnly = cms.bool(True),
                                                ignoreHtMiss = cms.bool(False)
                                                )




# ---------------------------------------------------------------------
# Produce Ntuple Module
# ---------------------------------------------------------------------

HLT_name = 'HLT'


process.load("EGamma.ECGelec.NtupleProducer_custom_cfi")
from EGamma.ECGelec.NtupleProducer_custom_cfi import *
process.produceNtuple = produceNtupleCustom.clone()


process.produceNtuple.NadL1M = cms.untracked.bool(True)
process.produceNtuple.NadTP = cms.untracked.bool(True)
process.produceNtuple.NadTPemul = cms.untracked.bool(True) # Need to put True when running Emulator !!
process.produceNtuple.NadTPmodif = cms.untracked.bool(False)
process.produceNtuple.PrintDebug = cms.untracked.bool(False)
#process.produceNtuple.PrintDebug = cms.untracked.bool(True)

process.produceNtuple.type = 'DATA'
process.produceNtuple.AOD = cms.untracked.bool(False)
process.produceNtuple.FillSC = cms.untracked.bool(True)
process.produceNtuple.functionName = cms.string("EcalClusterEnergyUncertainty")
# Trigger Stuff
process.produceNtuple.HLTTag          = 'TriggerResults::' + HLT_name
process.produceNtuple.TriggerEventTag = 'hltTriggerSummaryAOD::' + HLT_name
process.produceNtuple.HLTElePaths = cms.vstring(
   # 'HLT_Ele12_CaloIdL_TrackIdL_IsoVL_v',

'HLT_Ele17_CaloIdL_TrackIdL_IsoVL_v1',
'HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v2',
'HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_v2'
        )
process.produceNtuple.HLTMuonPaths    = cms.vstring('HLT_Mu9')
process.produceNtuple.HLTFilters      = cms.VInputTag('hltL1NonIsoHLTNonIsoSingleElectronEt17TighterEleIdIsolTrackIsolFilter::'+HLT_name,
                                                      'hltL1NonIsoHLTNonIsoDoubleElectronEt17PixelMatchFilter::'+HLT_name,
                                                      #'hltL1NonIsoHLTNonIsoSingleElectronEt17TightCaloEleIdEle8HEPixelMatchFilter::'+HLT_name,
                                                      'hltL1NonIsoHLTNonIsoSingleElectronEt17TighterEleIdIsolPixelMatchFilter::'+HLT_name,
                                                      'hltL1NonIsoHLTNonIsoSingleElectronEt17TightCaloEleIdEle8HEDoublePixelMatchFilter::'+HLT_name,
                                                      # Muon Trigger
                                                      'hltSingleMu9L3Filtered9')
process.produceNtuple.eleVetoIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-veto")
process.produceNtuple.eleLooseIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-loose")
process.produceNtuple.eleMediumIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-medium")
process.produceNtuple.eleTightIdMap = cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-tight")




process.L1TSeq = cms.Sequence(   process.RawToDigi        
#                                   + process.L1TReEmulateFromRAW
                                                      
)

# ---------------------------------------------------------------------
# Sequence PATH
# ---------------------------------------------------------------------
process.p = cms.Path (
    process.L1TSeq
    + process.kt6PFJets
    + process.egmGsfElectronIDSequence
    + process.ecalEBunpacker
    + process.simEcalTriggerPrimitiveDigis
    #+ process.simRctDigis
    #+ process.simGctDigis
    #+ process.simGtDigis
    + process.caloStage1FinalDigis
    + process.caloStage1LegacyFormatDigis
    #+ process.l1extraParticles
    + process.l1extraParticlesOnline
    + process.rawCaloStage2Digis
    + process.produceNtuple
    )


process.TFileService = cms.Service ("TFileService",
                                    fileName = cms.string ("tree_testFastSim_TPG_checknow_debug_18_18_new.root")
                                    )
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
#process.schedule = cms.Schedule( process.p, process.output_step)
#process.schedule = cms.Schedule( process.p)
process.schedule.append(process.p)
#process.schedule = cms.Schedule( process.p,process.e)
#pythonDump = open("dump_cfg.py", "write")
#print >> pythonDump, process.dumpPython()


