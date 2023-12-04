from src.main import w_main
from src.file.service import check_and_download_files
check_and_download_files()

#  pyinstaller --onefile --noconsole --noconfirm -n pytimetracker -w main.py
# add tag
w_main.main()

