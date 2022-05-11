from cx_Freeze import setup, Executable
import core.constant as const
import os


def gen_exe():
    setup(
        name=const.PROGRAM_NAME,
        version=const.VERSION,
        description=const.DESCRIPTION,
        author="DedaleTeam",
        executables=[
            Executable(
                "main.py",
                base='Win32GUI',
                shortcutDir=os.path.join("..", "build"),
                targetName=f'{const.PROGRAM_NAME}.exe',
                icon="icon.ico",
                 )
        ],
        options={
                'build_exe': {
                            'excludes': [
                                'lib2to3',
                            ],
                            'includes': [
                                'core',
                            ],
                            'packages': [
                            ],
                            'include_files': [
                                # 'User Manual.pdf',
                                # 'icon.ico'
                            ],
                            'optimize': 2,
                            'include_msvcr': True,
                        },
        }
    )


if __name__ == '__main__':
    gen_exe()
