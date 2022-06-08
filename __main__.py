import sys

if __name__ == '__main__':
    # Get users current python version
    major_number = sys.version_info[0]
    minor_number = sys.version_info[1]

    # Check if the user is atleast using python 3.6
    if major_number < 3 or (major_number == 3 and minor_number < 6):
        print(f"""
                Current python version is {major_number}.{minor_number}\n
                Poirot requires python version 3.6 or later
                """)
        sys.exit(1)

    # If they are using a valid version of python then start the main code
    import poirot
    poirot.main()