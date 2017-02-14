#!/bin/bash

# Install the pip utility for python modules administration
echo "--------->  Installing pip"
sudo apt-get install python-pip

# Install python modules required by eloi_twit
echo "--------->  Install python modules required by eloi_twit"
sudo pip install numpy --upgrade
sudo pip install matplotlib --upgrade
sudo pip install scipy --upgrade
sudo pip install twitter --upgrade
sudo pip install argparse --upgrade
