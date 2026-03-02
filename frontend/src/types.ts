export type Lot = {
    date: string;
    order: number;
    price: number;
    shares: number;
    shares_acc: number;
};

export type Holding = {
    lots: Lot[];
    cost: number;
    cost_per_share: number;
    id: string;
    max_price: number;
    min_price: number;
    previous_close: {
        price: number;
        t: number;
    };
    shares: number;
};
