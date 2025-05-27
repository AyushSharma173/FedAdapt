#!/bin/bash

# Set FedScale Home
export FEDSCALE_HOME=$(pwd)

if [[ $(uname -s) == 'Darwin' ]]; then
  echo "MacOS detected."
  echo "Setting FEDSCALE_HOME in bash profile..."
  echo export FEDSCALE_HOME=$(pwd) >> ~/.bash_profile
  echo alias fedscale=\'bash ${FEDSCALE_HOME}/fedscale.sh\' >> ~/.bash_profile
fi

# Install Miniconda if not installed
if ! command -v conda &> /dev/null
then
  echo "Installing Miniconda..."
  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
  bash Miniconda3-latest-MacOSX-arm64.sh -b -p $HOME/miniconda
  export PATH=$HOME/miniconda/bin:$PATH
fi

# Create conda environment manually
echo "Creating fedscale environment with python=3.10..."
conda create -n fedscale python=3.10 -y
conda activate fedscale

# Install dependencies manually
echo "Installing dependencies..."
conda install numpy pandas matplotlib scipy scikit-learn tqdm pyyaml -y
pip install gdown
pip install torch torchvision torchaudio
pip install tensorflow-macos
pip install tensorflow-metal

# Install fedscale itself
echo "Installing FedScale in editable mode..."
pip install -e .

echo "FedScale installation finished!"
