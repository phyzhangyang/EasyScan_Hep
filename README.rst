=======
EasyScan_HEP
=======

:EasyScan_HEP: A tool for easily connecting programs to scan parameter space of high energy physics models
:Author: Yang Zhang， Liangliang Shang
:Version: 0.1.0
:GitHub: https://github.com/phyzhangyang/EasyScan_HEP
:Website: https://easyscanhep.hepforge.org
:Documentation: https://arxiv.org/pdf/190X.XXXXX.pdf


Installation instructions
-------------------------

EasyScan_HEP is a Python3 code with dependencies on *numpy*, *scipy* and *ConfigParser* libraries. The optional plot functions and MultiNest sampler further require *matplotlib*, *pandas* and *pymultinest* libraries. The dependencies can be installed via pip:
:: 
    sudo apt install python3-pip python3-tk 
    
    sudo pip3 install numpy scipy matplotlib ConfigParser pandas pymultinest

The "easyscan.py" in folder "bin" is the main program, which is executed with configuration file through the command line,
::
    ./bin/easyscan.py templates/example_random.ini

Here *example_random.ini* is an example configuration file provided in EasyScan_HEP. It performs a scan on a simplified model,
:：
    f(x,y) = sin^2 x + cos^2 y,
    
using random sampler, where *x* and *y* are input parameters in range *[0,\pi]* and *[-\pi,\pi]*, respectively, and *f* is output parameter. 

Three other example configuration files in *templates* folder (*example_grid.ini*, *example_mcmc.ini* and *example_multinest.ini*) exhibit briefly usages of other samplers in EasyScan_HEP.

Configuration file *templates/LDM_MSSM.ini* is an simply physical examples. Relevant programs need to be installed beforehand, using
::
    cd utils
    make
and then it can be executed with 
::
    ./bin/easyscan.py templates/LDM_MSSM.ini

