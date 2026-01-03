"use strict";
class Cart {
    constructor(base_url = '') {
        Object.defineProperty(this, "base_url", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: base_url
        });
        Object.defineProperty(this, "csrfToken", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        const token = document.currentScript.dataset.csrfToken;
        if (token)
            this.csrfToken = token;
        else
            throw new Error('No csrf token provided');
    }
    async post(url = '', data = {}) {
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
        return await this.post();
    }
    async add(code, quantity = 1) {
        return await this.post(`add/${code}`, { quantity: quantity });
    }
    async update(id, quantity = 1) {
        return await this.post(`update/${id}`, { quantity: quantity });
    }
    async remove(id) {
        return await this.post(`remove/${id}`, {});
    }
    async clear() {
        return await this.post(`clear/`, {});
    }
}
const cart = new Cart();
//# sourceMappingURL=cart.js.map