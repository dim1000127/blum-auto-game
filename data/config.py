from data import secret_key

API_ID = secret_key.API_ID
API_HASH = secret_key.API_HASH

# delay between the start of the game on the account
ACC_DELAY = [5, 15]

# points each game
POINTS = [150, 200] #[min, max]

# minimum diamond balance
MIN_TICKETS = [50, 60] #[min, max]

DURATION_GAME = [30, 60] #[min, max]

# delay between game
SLEEP_GAME_TIME = [3, 8] #[min, max]

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30

HELLO_MESSAGE = '''
███████╗██╗░░░░░██╗██████╗░██████╗░███████╗██████╗░
██╔════╝██║░░░░░██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
█████╗░░██║░░░░░██║██████╔╝██████╔╝█████╗░░██████╔╝
██╔══╝░░██║░░░░░██║██╔═══╝░██╔═══╝░██╔══╝░░██╔══██╗
██║░░░░░███████╗██║██║░░░░░██║░░░░░███████╗██║░░██║
╚═╝░░░░░╚══════╝╚═╝╚═╝░░░░░╚═╝░░░░░╚══════╝╚═╝░░╚═╝
'''