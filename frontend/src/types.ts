export type Transaction = {
    date: string;
    price: number;
    shares: number;
};

export type Buy = Transaction & {
    type: 'BUY';
};

export type Sell = Transaction & {
    type: 'SELL';
};

export type Holding = {
    ticker: string;
    transactions: (Buy | Sell)[];
};
