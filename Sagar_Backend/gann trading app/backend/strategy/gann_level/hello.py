import os

def create_init_files(directory):
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            init_file = os.path.join(root, dir, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w'):
                    pass  # Create an empty __init__.py file

if __name__ == "__main__":
    create_init_files(r'C:\Users\pegas\OneDrive\Desktop\gann trading app\backend')
