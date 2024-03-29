from openpyxl import load_workbook
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
import config
import os
import numpy as np
import matplotlib.pyplot as plt

def append_df_to_excel(filename, df, sheet_name='Sheet1', startrow=None ,index=False ,header=False , **to_excel_kwargs):
    """
    Append a DataFrame [df] to existing Excel file [filename]
    into [sheet_name] Sheet.
    If [filename] doesn't exist, then this function will create it.

    Parameters:
      filename : File path or existing Excel file
                 (Example: '/path/to/file.xlsx')
      df : dataframe to save to workbook
      sheet_name : Name of sheet which will contain DataFrame.
                   (default: 'Sheet1')
      startrow : upper left cell row to dump data frame.
                 Per default (startrow=None) calculate the last row
                 in the existing DF and write to the next row...
      to_excel_kwargs : arguments which will be passed to `DataFrame.to_excel()`
                        [can be a dictionary]

    Returns: None

    (Example)
    append_df_to_excel('output.xlsx', df)

    """
    # Load existing workbook or create a new one
    try:
        wb = load_workbook(filename)
    except FileNotFoundError:
        wb = Workbook()
        wb.save(filename)

    # Check if sheet exists, if not create it
    if sheet_name not in wb.sheetnames:
        wb.create_sheet(sheet_name)

    # Get the active sheet
    sheet = wb[sheet_name]

    # Calculate starting row
    if startrow is None:
        startrow = sheet.max_row if sheet.max_row > 0 else 1

    # Convert the DataFrame to rows
    # rows = list(dataframe_to_rows(df, header=True))
    rows = list(dataframe_to_rows(df, index=index, header=header))

    # Write DataFrame rows to Excel sheet
    for row in rows:
        sheet.append(row)

    # Save the workbook
    wb.save(filename)

def save_detailed_results(script_name, Vx, Vy, elapsed_time, start_row=1, sheet_name='result'):
    """
    Save the detailed computation results to an Excel file.

    :param filename: str, name of the Excel file.
    :param script_name: str, name of the script/method used.
    :param Vx: list, location data.
    :param Vy: list, inventory data.
    :param elapsed_time: float, elapsed time of the computation.
    :param start_row: int, start row for the first DataFrame.
    :param sheet_name: str, sheet name to write the data into.
    """
    # 创建DataFrame来组织数据
    costs_df = pd.DataFrame([[script_name, elapsed_time]], columns=['Method', 'Costs'])
    location_df = pd.DataFrame(Vx)
    inventory_df = pd.DataFrame(Vy).T
    elapsed_time_df = pd.DataFrame([['Elapsed time', elapsed_time]])

    # Save costs data
    append_df_to_excel(config.Input_file, costs_df, sheet_name=sheet_name, index=False, header=False, startrow=start_row)

    # Calculate next start column for location data
    location_startcol = costs_df.shape[1] + 2  # Assuming 2 column gap for readability
    append_df_to_excel(config.Input_file, location_df, sheet_name=sheet_name, index=True, header=True, startrow=start_row, startcol=location_startcol)

    # Calculate next start column for inventory data
    inventory_startcol = location_startcol + location_df.shape[1] + 2  # Assuming 2 column gap for readability
    append_df_to_excel(config.Input_file, inventory_df, sheet_name=sheet_name, index=True, header=True, startrow=start_row, startcol=inventory_startcol)

    # Calculate start row for elapsed time data
    elapsed_time_startrow = start_row + max(costs_df.shape[0], inventory_df.shape[0], location_df.shape[0]) + 2  # Assuming 2 row gap for readability
    append_df_to_excel(config.Input_file, elapsed_time_df, sheet_name=sheet_name, index=True, header=True, startrow=elapsed_time_startrow)
    
    print("Detailed results have been saved to Excel.")

def save_and_print_results(script_name, IS, NS, MS, SS_SAA, opt_f, elapsed_time):
    """
    Save results to an Excel file and print them.

    :param script_name: str, name of the script/method used.
    :param IS: int, input size parameter.
    :param NS: int, number of simulations/iterations/etc.
    :param opt_f: float, the optimized function value.
    :param elapsed_time: float, time taken for the operation in seconds.
    """
    # 创建一个DataFrame来组织需要输出的数据
    result_df = pd.DataFrame([[script_name, IS, NS, MS, SS_SAA, float(opt_f), elapsed_time]])

    # 将数据输出到Excel的特定列，只有一列
    append_df_to_excel(config.Output_file, result_df, sheet_name='results', index=False, header=False, startrow=0)

    # 打印结果
    print(f"Method: {script_name}")
    print(f"I: {IS}, S: {NS}, M: {MS}, N: {SS_SAA}")    
    print(f"Costs: {float(opt_f)}")
    print(f"Elapsed time: {elapsed_time} seconds.")


def plot_cluster_sampling(demand_transformed, cluster_labels, sample, save_directory, script_name, m):
    
    # 绘制聚类结果和分层采样的样本点
    plt.figure(figsize=(10, 8),dpi=300)
    for i, label in enumerate(np.unique(cluster_labels)):
        plt.scatter(
            demand_transformed[cluster_labels == label, 0],
            demand_transformed[cluster_labels == label, 1],
            label=f'Cluster {i}'
        )

    # 假设sample包含了所有采样点的索引
    for s in sample:
        plt.scatter(
            demand_transformed[s, 0],
            demand_transformed[s, 1],
            c='red', # 标记颜色
            edgecolor='k',
            marker='x', # 标记样式
            s=100 # 设置标记大小为100 point^
        )

    plt.title('Stratified Sampling of Clusters')
    plt.xlabel('PCA Feature 1')
    plt.ylabel('PCA Feature 2')
    plt.legend()

    # 保存图片到指定目录
    plt.savefig(os.path.join(save_directory, f'{script_name}_sample_{m+1}.jpg'), format='jpg')
    # plt.close()  # 关闭图形界面，防止内存泄露