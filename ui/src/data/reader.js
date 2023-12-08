import fs from 'fs';
import {parse} from 'csv-parse';

export function read_kline_csv(fname) {
    const data = [];
    fs.createReadStream(fname)
        .pipe(parse({ delimiter: ',' }))
        .on('data', (r) => {
            data.push(r);
        })
        .on('end', () => {
            console.log(data);
        });
    return data;
}
