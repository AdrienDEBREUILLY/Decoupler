import xlrd
import xlsxwriter
import csv
import core.constant as const
import wx


def read(file_path: str, sheet_number: int = 0, initial_header=False) -> tuple or list:
    my_book = xlrd.open_workbook(file_path)
    sheet = my_book.sheet_by_index(sheet_number)
    line_count = sheet.nrows
    column_count = sheet.ncols
    # print(f"total : {line_count}, total : {column_count}")

    header = [sheet.cell_value(0, j) for j in range(column_count)]
    # header = list()
    # for j in range(column_count):
    #     value = sheet.cell_value(0, j)
    #     header.append(value)

    simplified_header = [text.replace(" ", "").replace("\n", "").replace("\t", "").upper() for text in header]
    #  a = list()
    #  for text in header:
    #      a.append(text.replace(" ", "").replace("\n", "").replace("\t", "").upper())

    data = list()
    for i in range(1, line_count):
        row = dict()
        for j in range(column_count):
            value = sheet.cell_value(i, j)
            key = simplified_header[j]
            row[key] = value
        data.append(row)

    if initial_header:
        # origin header est utiliser
        return data, simplified_header, header
    # origin header n'est pas utiliser
    return data


def read_csv(file_path: str):
    data = list()
    with open(file_path) as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data.append(row)
    return data


def write(file_path: str, data_list: list, ordored_header_upper: list, ordored_header: list,
          progressbar: wx.ProgressDialog):
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()
    # define_format
    header_style = workbook.add_format()
    header_style.set_bg_color(const.CELL_FORMAT_HEADER["bg_color"])
    header_style.set_bold(const.CELL_FORMAT_HEADER["bold"])
    # modified_style
    modified_style = workbook.add_format()
    modified_style.set_bg_color(const.CELL_FORMAT_MODIFIED_CELL["bg_color"])
    modified_style.set_bold(const.CELL_FORMAT_MODIFIED_CELL["bold"])
    # write header
    for i in range(len(ordored_header_upper)):
        value = ordored_header[i]
        worksheet.write(0, i, value, header_style)
    # write data
    progressbar.SetRange(len(data_list))
    row_count = 1
    for nline in range(len(data_list)):
        row = data_list[nline]
        progressbar.Update(nline, "[2/2] Writing datas")
        for i in range(len(ordored_header_upper)):
            key = ordored_header_upper[i]
            value = row[key]
            if key in row["Decoupleur_Status"]:
                worksheet.write(row_count, i, value, modified_style)
            else:
                worksheet.write(row_count, i, value)
        row_count += 1
    workbook.close()
