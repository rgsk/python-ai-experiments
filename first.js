const replaceToCsvWithEncodedString = (codeStr) => {
  return codeStr.replace(
    /data\.to_csv\(["']([^"']+)["'](.*)\)/g,
    (match, fileName, args) => {
      const cleanedArgs = args.trim().replace(/^,/, ""); // Remove leading comma and space
      return `
  file_name = '${fileName}'
  name_delimiter = '<name>'
  line_delimiter = '<line>'
  csv_data = data.to_csv(${cleanedArgs}).replace('\\n', line_delimiter)
  single_line = f'{file_name}{name_delimiter}{csv_data}'
  print(single_line)
      `.trim();
    }
  );
};

// Example usage:
const codeExample = `
  import pandas as pd
  data = pd.DataFrame({'x': [1, 2, 3], 'y': [2, 4, 6]})
  data.to_csv("linear_regression_sample_data.csv", index=False, header=True)
  `;

console.log(replaceToCsvWithEncodedString(codeExample));
