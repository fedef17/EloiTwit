#!/bin/bash

# Install the pip utility for python modules administration
echo "--------->  Installing pip"
sudo apt-get install python
sudo apt-get install build-essential
sudo apt-get install python-setuptools
sudo apt-get install python-wheel
sudo apt-get install python-pip
sudo apt-get install python-tk

# Install python modules required by eloi_twit
echo "--------->  Install python modules required by eloi_twit"
sudo pip install numpy --upgrade
sudo pip install matplotlib --upgrade
sudo pip install scipy --upgrade
sudo pip install twitter --upgrade
sudo pip install argparse --upgrade
