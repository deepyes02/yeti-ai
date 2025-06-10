from dotenv import load_dotenv

def load_environment_variables():
  """
  Load environment variables and also connect with langsmith so make sure this function is only called when requierd.
  """
  load_dotenv()