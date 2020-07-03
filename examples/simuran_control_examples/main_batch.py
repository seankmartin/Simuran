from simuran.batch_setup import BatchSetup


def main(in_dir):
    batch_setup = BatchSetup(in_dir)
    print(batch_setup)
    batch_setup.write_batch_params(True)


if __name__ == "__main__":
    in_dir = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSCa1_muscimol"
    main(in_dir)
