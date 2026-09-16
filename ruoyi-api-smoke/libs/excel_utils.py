#封装读excel表
import openpyxl
from config.config import PATH,SHEET_NAME

def read_excel(path = PATH,sheet_name = SHEET_NAME):

    
    #========以下代码无需修改====================
    workbook = openpyxl.load_workbook(path) 

    #选择表
    worksheet = workbook[sheet_name]

    #读数据⭐
    #zip()-->把可迭代对象打包成元祖
    data = []
    keys = [cell.value for cell in worksheet[3]]#拿key行，生成key列表

    for row in worksheet.iter_rows(min_row=4,values_only=True): #从第四行开始拿数据，只返回值

        dict_data = dict(zip(keys,row))
        #如果读取的字段is true == true ，则append，否则不返回到结果
        if dict_data['is_true']:
            data.append(dict_data)
            
        
            

    #关闭excel
    workbook.close()
    
    return data
#===================================================

# if __name__ == "__main__":
#     result = read_excel()
#     print(result)