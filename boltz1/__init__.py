# ***************************************************************************
# *
# * Authors:     you (you@yourinstitution.email)
# *
# * your institution
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# ***************************************************************************
import os
import pwem
from boltz1.constants import BOLTZ1, BOLTZ1_ENV_NAME, BOLTZ1_DEFAULT_VERSION
from pyworkflow.utils import runJob

__version__ = "0.0.1"  # Plugin version

_logo = "icon.png"
_references = ['boltz12025']

V1 = "0.4.1"

class Plugin(pwem.Plugin):
    _url = "https://github.com/scipion-em/scipion-em-boltz1"
    _supportedVersions = [V1]  # Binary version

    @classmethod
    def getEnvActivation(cls):
        return f"conda activate boltz1_env"

    @classmethod
    def getEnviron(cls, gpuID=None):
        """ Setup the environment variables needed to launch the program. """
        import pyworkflow.utils as pwutils
        environ = pwutils.Environ(os.environ)
        if 'PYTHONPATH' in environ:
            # this is required for python virtual env to work
            del environ['PYTHONPATH']

        if gpuID is not None:
            environ["CUDA_VISIBLE_DEVICES"] = gpuID

        return environ

    @classmethod
    def getBoltzProgram(cls, program):
        cmd = '%s %s && python %s' % (cls.getCondaActivationCmd(), cls.getEnvActivation(), program)
        return cmd

    @classmethod
    def getCommand(cls, program, args):
        return cls.getBoltzProgram(program) + args

    @classmethod
    def getBoltzEnvActivation(cls):
        return "conda activate boltz1-%s" %BOLTZ1_DEFAULT_VERSION

    @classmethod
    def defineBinaries(cls, env):
        def getBoltzInstallationCommands():
            commands = cls.getCondaActivationCmd() + " "
            # Remove existing conda environment if it exists
            commands += ' conda create -y -n %s -c conda-forge python=3.10 && ' %BOLTZ1_ENV_NAME
            # Create the conda environment
            commands += 'conda activate %s && ' %BOLTZ1_ENV_NAME
            # Clone the Boltz-1 repository
            commands += "pip install boltz==%s -U &&" %BOLTZ1_DEFAULT_VERSION
            # Create a file to indicate that Boltz-1 has been installed
            commands += "touch boltz1_installed"
            return commands

        installCmds = [(getBoltzInstallationCommands(), "boltz1_installed")]
        env.addPackage(BOLTZ1, version=BOLTZ1_DEFAULT_VERSION, tar='void.tgz', commands=installCmds, default=True)

    @classmethod

    def runBoltz(cls, protocol, boltz1, args, cwd=None):
        """ Run Boltz-1 command from a given protocol. """
        fullProgram = '%s %s && %s' % (cls.getCondaActivationCmd(),
                                       cls.getBoltzEnvActivation(), boltz1)
        protocol.runJob(fullProgram, args, env=cls.getEnviron(), cwd=cwd,
                        numberOfMpi=1)