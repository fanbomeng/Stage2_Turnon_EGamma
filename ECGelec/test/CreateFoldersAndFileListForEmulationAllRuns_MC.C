#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include <TSelector.h>
#include <iostream>
#include <map>
#include <TLorentzVector.h>
#include <TH1.h>
#include <TH2.h>
#include <TH3.h>
#include <TMath.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TPaveText.h>
#include <TStyle.h>
#include <TROOT.h>
#include <sstream>
#include <TBranchElement.h>
#include <fstream>
#include <TROOT.h>
#include <TSystem.h>

using namespace std;


void Create()
{

  
  Bool_t CopyFiles = kTRUE;
  Bool_t Run = kTRUE;
  TString Stream = "DY_l1t_integr_v48.1_nocal_10.05.2016";
  TString Outfile = "filelist_AOD_";
  Outfile += Stream;
  Outfile += ".txt";
  TString RmQuery = "rm ";
  RmQuery += Outfile;
  gSystem->Exec(RmQuery.Data());
  TString ExecQuery = "python ./das_client.py --query=\"file dataset=/DYToEE_M-50_Tune4C_13TeV-pythia8/Phys14DR-PU40bx25_tsg_castor_PHYS14_25_V1-v2/AODSIM\" --limit=0 >> ";
  ExecQuery += Outfile ;
  gSystem->Exec(ExecQuery.Data());

  int numLines = 0;
  ifstream in(Outfile.Data());
  std::string unused;
  while ( std::getline(in, unused) )
    ++numLines;
  
  cout<<"Number of files = "<<numLines<<endl;
  
  cout<<"Creating folders and files..."<<endl;
  
  std::ifstream infile(Outfile.Data());
  std::string line;
  
  int fileId = 0;
  
  while (std::getline(infile, line))
    {
      ++fileId;
      
      //if(fileId>1) continue;
      
      //read line
      std::istringstream iss(line);
      string currentFilename ;
      iss >> currentFilename;
      cout<<"currentFilename = "<<currentFilename<<endl;
      
      //create folder
      TString MainFolderQuery = "mkdir ";
      MainFolderQuery += Stream;
      gSystem->Exec(MainFolderQuery);
      
      TString FolderQuery = "mkdir ";
      FolderQuery += Stream;
      FolderQuery += "/";
      stringstream ss;
      ss << fileId;
      TString temp = "";
      temp = TString(ss.str());
      FolderQuery += temp;
      gSystem->Exec(FolderQuery);
      
      // TString CopyExec = "./";
      // CopyExec += CopyFileName;
      // gSystem->Exec(CopyExec.Data());
      
      //create txt file
      TString FileListName = Stream;
      FileListName += "/";
      FileListName += temp;
      FileListName += "/filelist.txt";
      
      //fill txt file with current line
      ofstream myfile;
      myfile.open (FileListName.Data());
      myfile << line;
      myfile.close();

      //Create secondary file list
      TString Outfile2 = "filelist_GEN_SIM_RAW_";
      Outfile2 += temp;
      Outfile2 += ".txt";
      TString ExecQuery2 = "python ./das_client.py --query=\"parent file=";
      ExecQuery2 += currentFilename;
      ExecQuery2 += "\" --limit=0 >> ";
      ExecQuery2 += Stream;
      ExecQuery2 += "/";
      ExecQuery2 += temp;
      ExecQuery2 += "/";
      ExecQuery2 += Outfile2 ;
      gSystem->Exec(ExecQuery2.Data());


      /*std::ifstream infile2((Stream+"/"+temp+"/"+Outfile2).Data());
      std::string line2;
      
      TString Outfile3 = "filelist_GEN_SIM_RAW_";
      Outfile3 += temp;
      Outfile3 += ".txt";  

      while (std::getline(infile2, line2))
	{

	  std::istringstream iss2(line2);
	  string currentFilename2 ;
	  iss2 >> currentFilename2;
	  cout<<"currentFilename2 = "<<currentFilename2<<endl;


	  TString ExecQuery3 = "python ./das_client.py --query=\"parent file=";
	  ExecQuery3 += currentFilename2;
	  ExecQuery3 += "\" --limit=0 >> ";
	  ExecQuery3 += Stream;
	  ExecQuery3 += "/";
	  ExecQuery3 += temp;
	  ExecQuery3 += "/";
	  ExecQuery3 += Outfile3 ;
	  gSystem->Exec(ExecQuery3.Data());

	  }*/
      
      //create sh file
      TString ScriptName = Stream;
      ScriptName += "/";
      ScriptName += temp;
      ScriptName += "/script.sh";

      //Launch command on tier3
      ////Create script
      //fill txt file with current line
      ofstream myscript;
      myscript.open (ScriptName.Data());
      TString ChmodExec = "chmod 740 ";
      ChmodExec += ScriptName;
      gSystem->Exec(ChmodExec.Data());
      cout<<"ChmodExec = "<<ChmodExec<<endl;
      
      myscript << "#!/bin/bash\n";
      myscript << "cd /home/llr/cms/strebler/CMSSW_8_0_7_l1t_integr_v48.1/src/\n";
      myscript << "export SCRAM_ARCH=slc6_amd64_gcc493\n";
      myscript << "source /opt/exp_soft/cms/cmsset_default.sh\n";
      myscript << "eval `scramv1 runtime -sh`\n";
      myscript << "export X509_USER_PROXY=~/.t3/proxy.cert\n";
      myscript << "cd EGamma/ECGelec/test/" << Stream ;
      myscript <<"/";
      myscript << temp;
      myscript << "\n";
      myscript << "cmsRun ../../eleTreeProd_Stage2_new807_MC.py inputFiles=";
      myscript << currentFilename ;
      myscript << " secondaryFilesList="<<Outfile2;

      //trimed currentFilename
      string x=currentFilename;
      int pos = x.find("00000/");
      string sub = x.substr (pos+6);
      cout<<sub<<endl;
      myscript.close();   

      // TString CdExec = "cd ";
      // CdExec += Stream ;
      // CdExec += "/";
      // CdExec += temp;
      // CdExec += "/";
      TString LaunchExec = "/opt/exp_soft/cms/t3/t3submit ";
      //TString LaunchExec = "source /opt/exp_soft/cms/t3/t3setup ; /opt/exp_soft/cms/t3/t3submit ";
      LaunchExec += Stream ;
      LaunchExec += "/";
      LaunchExec += temp;
      LaunchExec += "/";
      LaunchExec += "script.sh";
      if(Run) gSystem->Exec(LaunchExec.Data());
    }
  
  
      /*
      std::ifstream infile2(Outfile.Data());
      std::string line2;
      fileId = 0;
      cout<<fileId<<endl;

      
      while (std::getline(infile2, line2))
	{
	  ++fileId;
	  if(fileId > 0)
	    // if(fileId > 310 && fileId <= 319 && CopyFiles)
	    {
	      //cout<<"fileId = "<<fileId<<endl;
	      //read line
	      std::istringstream iss(line2);
	      string currentFilename ;
	      iss >> currentFilename;
	      //cout<<"currentFilename = "<<currentFilename<<endl;

	      stringstream ss;
	      ss << fileId;
	      TString temp = "";
	      temp = TString(ss.str());
	      //cout<<"temp = "<<temp<<endl;

	      //copy file
	      TString Copy = "xrdcp root://xrootd.unl.edu/";
	      Copy += currentFilename ;
	      Copy += " ";
	      Copy += Stream;
	      Copy += "/";
	      Copy += temp;
	      Copy += "/";
	      //cout<<"Copy = "<<Copy<<endl;

	      //trimed currentFilename
	      string x=currentFilename;
	      int pos = x.find("00000/");
	      string sub = x.substr (pos+6);
	      //cout<<"Sub = "<<sub<<endl;

	      Copy = "ln -fs /data_CMS/cms/davignon/Trigger_myOwnFork_WithThomasUpdates2/CMSSW_7_6_0_pre7/src/L1Trigger/L1TNtuples/SingleMuon/";
	      Copy += temp ;
	      Copy += "/";
	      Copy += sub;
	      Copy += " ";
	      Copy += Stream;
	      Copy += "/";
	      Copy += temp;
	      Copy += "/.";

	      cout<<"Copy = "<<Copy<<endl;
	  

	      //create txt file
	      TString CopyFileName = "";
	      CopyFileName += Stream;
	      CopyFileName += "/";
	      CopyFileName += temp;
	      CopyFileName += "/copy.sh";
	      //cout<<"CopyFileName = "<<CopyFileName<<endl;
      
	      //fill txt file with current line
	      ofstream myfile;
	      myfile.open (CopyFileName.Data());
	      myfile << Copy;
	      myfile.close();           

	      TString ChmodCopy = "chmod 740 ";
	      ChmodCopy += CopyFileName ;
	      gSystem->Exec(ChmodCopy);

	      TString RmExec = "rm ";
	      RmExec += Stream;
	      RmExec += "/";
	      RmExec += temp;
	      RmExec += "/";
	      RmExec += sub;
	      //cout<<"RmExec = "<<RmExec<<endl;
	      gSystem->Exec(RmExec.Data());

	      TString CopyCmd = "nohup ./";
	      CopyCmd += Stream;
	      CopyCmd += "/";
	      CopyCmd += temp;
	      CopyCmd += "/copy.sh >> ";
	      CopyCmd += Stream;
	      CopyCmd += "/";
	      CopyCmd += temp;
	      CopyCmd += "/copy.log &";

	      //cout<<"CopyCmd = "<<CopyCmd<<endl;
	      // gSystem->Exec(CopyCmd.Data());
	    }
      

	}
      */
      
    
  
}

