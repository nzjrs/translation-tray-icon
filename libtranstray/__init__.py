import os.path

def is_installed():
    return not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "setup.py"))
            
    
