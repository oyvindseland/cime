#! /usr/bin/env python 
import sys, getopt, os 
import numpy as np 
import Nio 
import time
import utility

#
# Command options 
#
def disp_usage(callType):
    print '\n Sets up CESM cases for either an ensemble of runs or a small (size 3)\n'
    print 'test set (default). Then Use pyCECT utilities to create an ensemble \n'
    print 'summary file or to evaluate the small test set of runs against the ensemble.\n'
    print '  '
    print '  ----------------------------'
    print '   Args for ensemble.py :'
    print '  ----------------------------'
    print '   ensemble.py'
    print '   -h                      : prints out this usage message'


    print 'Required flags:'
    if callType == 'single_run.py':
        print '  --case <name>    Case name passed on to create_newcase'
    else:
        print '  --case <name>    Case name passed on to create_newcase (must end in ".000")'
    print '  --mach <name>    Machine name passed on to create_newcase'
    print ' ' 
    print 'Optional flags (+ all "--" options to create_newcase): '
    print '  --project <num>  Project number to charge in job scripts'
    if callType == 'single_run.py':
       print '  --pertlim <num>     Run CAM with non-zero pertlim'
   print '  --walltime <hr:mn> Amount of walltime requested (default = 4:30, or 0:10 with --uf enabled)'
   print '  --compiler <name>  Compiler to use (default = same as Machine default) '
   print '  --compset <name>   Compset to use (default = F2000)'
   print '  --res <name>       Resolution to run (default = f19_f19)'
   print '  --uf               Enable ninth time step runs (ultra-fast mode) - otherwise the default is 12-month runs'
   if callType == 'ensemble.py': 
       print '  --nb               Disables auto building the root case of the ensemble.'
       print '  --ns               Disables auto submitting any members of the ensemble.'
       print '  --ensemble <size>  Build the ensemble (instead of building 3 cases with random pertlim values for verification),'
       print '                     and specify the number of ensemble members to generate (e.g.: 151 for annual averages or 350 for ultra-fast mode)'
   else:
       print '  --nb               Disables building (and submitting) the single case.'
       print '  --ns               Disables submitting the single case.'

########
def process_args_dict(caller, caller_argv):


   # Pull in and analyze the command line arguements
    s='case= mach= project= compiler= compset= res= uf nb ns ensemble= verbose silent test multi-driver pecount= nist= mpilib= pesfile= gridfile= srcroot= output-root= script-root= queue= user-modes-dir= input-dir= pertlim= walltime= h'

    optkeys=s.split()

    try: 
        opts, args = getopt.getopt(caller_argv,"hf:",optkeys)

    except getopt.GetoptError:
        disp_usage(caller)
        sys.exit(2)

    #check for help   
    for opt,arg in opts:
        if opt == '-h':
            disp_usage(caller)
            sys.exit()

    #opts_dict and defaults    
    opts_dict={}
    opts_dict['res']='f19_f19'
    opts_dict['compset']='F2000'
    opts_dict['walltime']='00:00'
    opts_dict['pertlim']= 0
    opts_dict['nb'] = False
    opts_dict['ns'] = False
    opts_dict['uf'] = False
    opts_dict['ensemble'] = 0
    #for create newcase
    opts_dict['verbose'] = False
    opts_dict['silent'] = False
    opts_dict['test'] = False
    opts_dict['multi-driver'] = False
    opts_dict['case'] = 'NONE'
    opts_dict['mach'] = 'NONE'

    s_case_flags = ''

    #opts_dict = utility.getopt_parseconfig(opts, optkeys, caller, opts_dict)
    for opt, arg in opts:
        if opt == '--case':
            opts_dict['case'] = arg
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--mach':
            opts_dict['mach'] = arg
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--project':
            opts_dict['project'] = arg
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--compset':
            opts_dict['compset'] = arg
            #required - add later
        elif opt == '--res':
            opts_dict['res'] = arg
            #required - add later
        elif opt == '--ensemble':
            opts_dict['ensemble'] = arg
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--compiler':
            opts_dict['compiler'] = arg
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--pertlim':
            opts_dict['pertlim'] = arg
            if caller == 'ensemble.py':
                print "WARNING: pertlim ignored for ensemble.py."
                opts_dict['pertlim'] = 0
            else:
                s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--project':
            opts_dict['project'] = arg
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--uf':
            opts_dict['uf'] = True
            s_case_flags += ' ' + opt 
        elif opt == '--nb':
            opts_dict['nb'] = True
            s_case_flags += ' ' + opt 
        elif opt == '--ns':
            opts_dict['ns'] = True
            s_case_flags += ' ' + opt 
        elif opt == '--verbose':
            opts_dict['verbose'] = True
            s_case_flags += ' ' + opt 
        elif opt == '--silent':
            opts_dict['silent'] = True
            s_case_flags += ' ' + opt 
        elif opt == '--test':
            opts_dict['test'] = True
            s_case_flags += ' ' + opt 
        elif opt == '--multi-driver':
            opts_dict['multi-driver'] = True        
            s_case_flags += ' ' + opt 
        elif opt == '--nist':
            opts_dict['nist'] = arg
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--pecount':
            opts_dict['pecount'] = arg     
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--mpilib':
            opts_dict['mpilib'] = arg
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--pesfile':
            opts_dict['pesfile'] = arg     
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--srcroot':
            opts_dict['srcroot'] = arg
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--output-root':
            opts_dict['output-root'] = arg     
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--script-root':
            opts_dict['script-root'] = arg     
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--queue':
            opts_dict['queue'] = arg     
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--input-dir':
            opts_dict['input-dir'] = arg     
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--user-modes-dir':
            opts_dict['user-modes-dir'] = arg     
            s_case_flags += ' ' + opt + ' ' + arg
        elif opt == '--walltime':
            opts_dict['walltime'] = arg     
            #add below

    #check required things: case, machine
    if opts_dict['mach'] == 'NONE':
        print('Error: Must specify machine (--mach)')
        sys.exit()
    if opts_dict['case'] == 'NONE':
        print('Error: Must specify case (--case)')
        sys.exit()
    if caller == 'ensemble.py':
        case = opts_dict['case']
        if case[-4:] != '.000':
            print('Error: when using ensemblee.py, the case name must end in ".000".'
            sys.exit()

    if opts_dict['walltime'] == '00:00':
        if opts_dict['uf'] == True:
            opts_dict['walltime'] = '00:10'
        else:
            opts_dict['walltime'] = '04:30'
    s_case_flags += '--walltime ' + opts_dict['walltime']              

    return opts_dict, s_case_flags

#######

def single_case(opts_dict, case_flags):
    
    #directory with single_run.py and ensemble.py
    root_dir = os.path.basename(__file__)

    #scripts dir
    ret = os.chdir(root_dir)
    ret = os.chdir('../../scripts')

    ##res and compset are required for create_newcase
    case_flags += '--compset ' + opts_dict[compset] + ' --res ' + opts_dict['res'] + ' -run-unsupported'

    #create newcase
    print('STATUS: create_newcase flags = ' + case_flags)
    command = './create_newcase ' + case_flags
    ret = os.system(command)

    #modify namelist settings 
    path_val = os.getcwd()
    path = path_val + '/' + opts_dict['case']
    ret = os.chdir(path)              
                  
    command = 'chmod u+w *'
    ret = os.system(command)

    command = 'cp env_run.xml env_run.xml.orig'
    ret = os.system(command)

    print("STATUS: Adjusting env_run.xml....")
    command = './xmlchange --file env_run.xml --id BFBFLAG --val TRUE'
    ret = os.system(command)
    command = './xmlchange --file env_run.xml --id DOUT_S --val FALSE'
    ret = os.system(command)
    command = './xmlchange --file env_run.xml --id REST_OPTION --val never'
    ret = os.system(command)

    #time steps
    if opts_dict['uf'] == True:
        command = './xmlchange --file env_run.xml --id STOP_OPTION --val nsteps'
        ret = os.system(command)
        command = '  ./xmlchange --file env_run.xml --id STOP_N --val 9'
        ret = os.system(command)
    else:
        command = './xmlchange --file env_run.xml --id STOP_OPTION --val nmonths'
        ret = os.system(command)
        command = './xmlchange --file env_run.xml --id STOP_N --val 12'
        ret = os.system(command)
        
    print('STATUS: running setup...')
    command = './case_setup'
    ret = os.system(command)
    
    print "STATUS: Adjusting user_nl_* files...."
    if os.path.isfile('user_nl_cam'] == True:
        if opts_dict['uf'] == True:
#   echo "avgflag_pertape = 'I'" >> user_nl_cam
#    echo "nhtfrq  = 9" >> user_nl_cam
        else
#    echo "avgflag_pertape = 'A'" >> user_nl_cam
#    echo "nhtfrq  = -8760" >> user_nl_cam
 


  echo "inithist = 'NONE'" >> user_nl_cam
  if [ ! "$PERTLIM" == "0" ]; then
    echo "pertlim = $PERTLIM" >> user_nl_cam
# Only edit user_nl_clm if the file exists (otherwise not using CLM!)
if [ -e user_nl_clm ]; then
  # Have CLM output everything (single precision)
  if [ $UF -eq 1 ]; then
    echo "hist_avgflag_pertape = 'I'" >> user_nl_clm
    echo "hist_nhtfrq  = 9" >> user_nl_clm
  else
    echo "hist_avgflag_pertape = 'A'" >> user_nl_clm
    echo "hist_nhtfrq  = -8760" >> user_nl_clm
  fi
fi



########
def main(argv):

    caller = 'single_run.py'

    opts_dict, case_flags = process_args_dict(caller, argv)




########
if __name__ == "__main__":
    main(sys.argv[1:])
