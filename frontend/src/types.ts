export type Buy = {
    date: string;
    price: number;
    shares: number;
    shares_acc: number;
};

export type Holding = {
    buys: Buy[];
    cost: number;
    cost_per_share: number;
    id: string;
    max_price: number;
    min_price: number;
    previous_close: number;
    shares: number;
};
