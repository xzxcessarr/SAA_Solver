import * as XLSX from 'xlsx';

/**
 * @description 读取表头信息
 */
export const useReadExcelHead = (sheet: XLSX.WorkSheet) => {
  const headers = [];
  const range = XLSX.utils.decode_range(sheet['!ref']!);
  const rowNum = range.s.r; // 通常是0，除非工作表不是从第一行开始的
  for (let colNum = range.s.c; colNum <= range.e.c; ++colNum) {
    const nextCell = sheet[XLSX.utils.encode_cell({ c: colNum, r: rowNum })];
    // 如果单元格存在并有内容，则使用单元格内容作为表头，否则使用默认列名
    let cellText = nextCell && nextCell.v ? nextCell.v.toString() : `Column${colNum + 1}`;
    headers.push(cellText);
  }
  return headers;
}

/**
 * @description 读取excel原数据
 */
export const useReadRawData = (rawFile: any, sheetName?: string) =>
  new Promise<{ header: string[]; excelData: any[]; sheetNames: string[] }>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e: ProgressEvent<FileReader>) => {
      try {
        const data = e?.target?.result;
        const workbook = XLSX.read(data, { type: 'array' });
        const sheetNames = workbook.SheetNames;
        const selectedSheetName = sheetName ? sheetName : sheetNames[0];
        const worksheet = workbook.Sheets[selectedSheetName];

        // 确保所有列都被读取, 使用 header: 1 选项生成数组的数组
        const rawData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
        const headers = useReadExcelHead(worksheet);
        // 转换数组的数组为对象数组
        const excelData = rawData.slice(1).map(row => {
          return headers.reduce((obj, header, index) => {
            obj[header] = row[index] || '';
            return obj;
          }, {});
        });

        resolve({ header: headers, excelData, sheetNames });
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = (error) => reject(error);
    reader.readAsArrayBuffer(rawFile);
  });

export default useReadRawData;