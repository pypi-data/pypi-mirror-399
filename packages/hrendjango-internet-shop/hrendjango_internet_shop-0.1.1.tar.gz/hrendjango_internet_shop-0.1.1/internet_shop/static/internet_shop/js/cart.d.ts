declare class Cart {
    base_url: string;
    csrfToken: string;
    constructor(base_url?: string);
    protected post(url?: string, data?: object): Promise<object>;
    all(): Promise<object>;
    add(code: string, quantity?: number): Promise<object>;
    update(id: string, quantity?: number): Promise<object>;
    remove(id: string): Promise<object>;
    clear(): Promise<object>;
}
declare const cart: Cart;
//# sourceMappingURL=cart.d.ts.map