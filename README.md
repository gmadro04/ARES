
# SWARM GENERATOR
SWARM GENERATOR is a experimental generator of missions to swarms robotics. SWARM GENERATOR provides an experimental set up, a repository of collective behaviors (software control) and a protocol to study swarms robots and their properties. 

[You can find more information about SWARM GENERATOR here](https://gmadro04.github.io/gmadro04/swarm_generator.html)
# INSTALLATION
In this section you will find materials and first instructions on how to prepare your computer please follow next steps to install everything you need to use SWARM GENERATOR. 

## Dependencies 

* [ARGoS3 (3.0.0-beta56)](https://www.argos-sim.info/core.php)

If you do not have installed Ubuntu the following tutorials will guide you step by step to install Ubuntu on your computer.

* [Installing the OS: Ubuntu 20.04.5 LTS (Focal Fossa) 64bit](https://releases.ubuntu.com/focal/)

### Installation of SWARM GENERATOR
Once installed ARGoS3 open the folder where ARGoS3 was installed. Now place the project folder into the folder.

```bash
    git clone https://github.com/GMadro04/SWARM_GENERATOR.git
```
### Compiling and Installing

Once placed the project folder, you must compile and install the shared library and header files in the system.

#### Setting up the code 

1. Enter the following commands in a terminal in order to prepare the code for the experiments.

```bash
cd remplace your path-ARGoS3/SWARM_GENERATOR
mkdir build
cmake ../src
make
```

2. Set the environment variable ARGOS_PLUGIN_PATH to the path in which the build/ directory is located.

```bash
export ARGOS_PLUGIN_PATH=$ARGOS_PLUGIN_PATH:$HOME/remplace your path-ARGoS3/SWARM_GENERATOR/build/
```

3. You can also put this line into your $HOME/.bashrc file, so it will be automatically executed every time you open a terminal. You add the line by entering the following command.

```bash
echo 'export ARGOS_PLUGIN_PATH=$ARGOS_PLUGIN_PATH:$HOME/remplace your path-ARGoS3/SWARM_GENERATOR/build/' >> ~/.bashrc
```
4. Now run the experiment to check if everything is OK.
```bash
cd ~/remplace your path-ARGoS3/SWARM_GENERATOR/
argos3 -c experimento.argos
```
If the usual ARGoS interface appears, you’re ready to go.

## How to use SWARM GENERATOR

SWARM GENERATOR provides launch scripts to start the experiments in a simulation on ARGoS3, process the results of experiments and generate a report with the results. The parameters of the launch scripts, such as the type of mission, type of control software, run experiments with/with out faults and control software (code collective behavior) must be set by editing the parameter sections of the following scripts.

| Script | Description |
| --- | --- |
| sub_experimental.py | Start the simulations with the desired parameters.To start the execution of experiments, run `python3 sub_experimental.py` or if you want to know how much time spent your computer in execute all experiments run `time python3 sub_experimental.py`.|
| loo_experimentalgenerator.py | This script generate all configuration for the experimental set up to run the simulation like the shape of scenario, size, time duration of the mission and others |
|processing_data.py| This scrip process all data collected after the execute all experiments, generate plots with the results of the performance for mission and swarm robots properties (Scalability, Robustez, Flexibility). All plots are saved into the folder "Plots-Experimentos". To start all processing data run `python3 processing_data.py` or if you want to know how much time spent your computer in process all data run `time python3 processing_data.py`|
|reporte.ipynb| This script generate a report for mission in a file HTML. To execute the notebook make sure that you are into the project folder and run `jupyter notebook reporte.ipynb` |

## ***¡¡ Important note !!***

* Before to run **sub_experimental.py** you have to set some params editing the script to specify the params of operation for the experiment. This params are type of mission, class of control software, operation with/ with out faults and the control software for the robots. **Into the script you can find the variables that you must edite** 

* Before generating the results report, you must specify the type of mission you want to see. Within the script you can find the variables that you must edit depending on the type of mission.

## Authors

- [Gabriel Mauricio Madroñero Pachajoa](https://github.com/GMadro04)
- [David Garzón Ramos](https://iridia.ulb.ac.be/~dgarzonramos/)

## Support
For support or any question, please fell free in contact me.