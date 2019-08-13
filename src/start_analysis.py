from analysis_part import XDFFile


if __name__ == "__main__":
    xdf = XDFFile("record/YUI/exp001/block_001.xdf")
    # xdf.showEEG()
    xdf.showET()