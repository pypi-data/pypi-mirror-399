class Cart {
    csrfToken: string;

    constructor(public base_url: string = '') {
        const token = document.currentScript!.dataset.csrfToken;
        if (token) this.csrfToken = token;
        else throw new Error('No csrf token provided');
    }

    protected async post(url: string = '', data: object = {}): Promise<object> {
        return await (await fetch(`${this.base_url}/cart/${url}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken,
            },
            body: JSON.stringify(data)
        })).json();
    }

    async all() {
        return await this.post()
    }

    async add(code: string, quantity: number = 1) {
        return await this.post(`add/${code}`, {quantity: quantity})
    }

    async update(id: string, quantity: number = 1) {
        return await this.post(`update/${id}`, {quantity: quantity})
    }

    async remove(id: string) {
        return await this.post(`remove/${id}`, {})
    }

    async clear() {
        return await this.post(`clear/`, {})
    }
}

const cart = new Cart();
