"""
SimASM - Abstract State Machine Framework for Discrete Event Simulation

A Python package for modeling, simulating, and verifying discrete event
systems using Abstract State Machines as the common semantic foundation.

Usage in Jupyter/Colab:
    import simasm  # Auto-registers %%simasm magic

    %%simasm model --name mm1_queue
    domain Event
    ...

    %%simasm experiment
    experiment Test:
        model := "mm1_queue"
        ...
    endexperiment

    %%simasm verify
    verification Check:
        ...
    endverification
"""

__version__ = "0.1.0"
__author__ = "Steve"


# Auto-register Jupyter magics when imported in IPython/Jupyter
def _register_jupyter_magics():
    """Auto-register magics if running in IPython/Jupyter."""
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            from simasm.jupyter.magic import SimASMMagics
            ipython.register_magics(SimASMMagics)
    except ImportError:
        pass  # IPython not installed
    except Exception:
        pass  # Not in IPython environment or other error


_register_jupyter_magics()
