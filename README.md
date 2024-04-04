
# SWARM GENERATOR
SWARM GENERATOR is a experimental generator of misions to swarms robotics. SWARM GENERATOR provies an experimental set up, a repository of collective behaviors (software control) and a protocol to study swarms robots and their properties. 



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