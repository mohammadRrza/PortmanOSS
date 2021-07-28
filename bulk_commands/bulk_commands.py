from Commands.get_backups import GetbackUp


if __name__ == '__main__':
    back_up = GetbackUp()
    print('Backup process is started.')
    back_up.run_command()
