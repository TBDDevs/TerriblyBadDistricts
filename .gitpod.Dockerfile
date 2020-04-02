
FROM gitpod/workspace-full
USER gitpod
# Install util tools.
RUN sudo apt-get update \
 && sudo apt-get install -y \
  apt-utils \
  git \
  less \
  wget

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O ~/miniconda.sh
RUN sudo bash ~/miniconda.sh -b -p $HOME/miniconda
RUN source $HOME/miniconda/bin/activate
RUN conda init
