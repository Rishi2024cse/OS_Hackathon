/**
 * E2EE Crypto Utils using Web Crypto API
 */

const CryptoUtils = {
    // Generate RSA-OAEP Key Pair for Encryption/Decryption
    async generateKeyPair() {
        return await window.crypto.subtle.generateKey(
            {
                name: "RSA-OAEP",
                modulusLength: 2048,
                publicExponent: new Uint8Array([1, 0, 1]),
                hash: "SHA-256",
            },
            true,
            ["encrypt", "decrypt"]
        );
    },

    // Export Public Key to PEM format
    async exportPublicKey(key) {
        const exported = await window.crypto.subtle.exportKey("spki", key);
        const body = btoa(String.fromCharCode(...new Uint8Array(exported)));
        return `-----BEGIN PUBLIC KEY-----\n${body}\n-----END PUBLIC KEY-----`;
    },

    // Export Private Key to PKCS8 format (Keep this in LocalStorage)
    async exportPrivateKey(key) {
        const exported = await window.crypto.subtle.exportKey("pkcs8", key);
        const body = btoa(String.fromCharCode(...new Uint8Array(exported)));
        return `-----BEGIN PRIVATE KEY-----\n${body}\n-----END PRIVATE KEY-----`;
    },

    // Import PEM Public Key
    async importPublicKey(pem) {
        const body = pem.replace(/-----BEGIN PUBLIC KEY-----|-----END PUBLIC KEY-----|\n/g, "");
        const binary = atob(body);
        const arrayBuffer = new ArrayBuffer(binary.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        for (let i = 0; i < binary.length; i++) {
            uint8Array[i] = binary.charCodeAt(i);
        }
        return await window.crypto.subtle.importKey(
            "spki",
            arrayBuffer,
            { name: "RSA-OAEP", hash: "SHA-256" },
            true,
            ["encrypt"]
        );
    },

    // Import PEM Private Key
    async importPrivateKey(pem) {
        const body = pem.replace(/-----BEGIN PRIVATE KEY-----|-----END PRIVATE KEY-----|\n/g, "");
        const binary = atob(body);
        const arrayBuffer = new ArrayBuffer(binary.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        for (let i = 0; i < binary.length; i++) {
            uint8Array[i] = binary.charCodeAt(i);
        }
        return await window.crypto.subtle.importKey(
            "pkcs8",
            arrayBuffer,
            { name: "RSA-OAEP", hash: "SHA-256" },
            true,
            ["decrypt"]
        );
    },

    // AES-GCM Key Generation
    async generateAESKey() {
        return await window.crypto.subtle.generateKey(
            { name: "AES-GCM", length: 256 },
            true,
            ["encrypt", "decrypt"]
        );
    },

    // Encrypt Message with AES-GCM
    async encryptMessage(message, aesKey) {
        const iv = window.crypto.getRandomValues(new Uint8Array(12));
        const encoded = new TextEncoder().encode(message);
        const ciphertext = await window.crypto.subtle.encrypt(
            { name: "AES-GCM", iv: iv },
            aesKey,
            encoded
        );
        return {
            ciphertext: btoa(String.fromCharCode(...new Uint8Array(ciphertext))),
            iv: btoa(String.fromCharCode(...iv))
        };
    },

    // Decrypt Message with AES-GCM
    async decryptMessage(encryptedBody, aesKey) {
        const ciphertext = new Uint8Array(atob(encryptedBody.ciphertext).split("").map(c => c.charCodeAt(0)));
        const iv = new Uint8Array(atob(encryptedBody.iv).split("").map(c => c.charCodeAt(0)));
        const decoded = await window.crypto.subtle.decrypt(
            { name: "AES-GCM", iv: iv },
            aesKey,
            ciphertext
        );
        return new TextDecoder().decode(decoded);
    },

    // RSA Wrap AES Key
    async wrapKey(aesKey, publicKey) {
        const exportedAES = await window.crypto.subtle.exportKey("raw", aesKey);
        const wrapped = await window.crypto.subtle.encrypt(
            { name: "RSA-OAEP" },
            publicKey,
            exportedAES
        );
        return btoa(String.fromCharCode(...new Uint8Array(wrapped)));
    },

    // RSA Unwrap AES Key
    async unwrapKey(wrappedAESBase64, privateKey) {
        const wrapped = new Uint8Array(atob(wrappedAESBase64).split("").map(c => c.charCodeAt(0)));
        const decryptedAES = await window.crypto.subtle.decrypt(
            { name: "RSA-OAEP" },
            privateKey,
            wrapped
        );
        return await window.crypto.subtle.importKey(
            "raw",
            decryptedAES,
            { name: "AES-GCM", length: 256 },
            true,
            ["encrypt", "decrypt"]
        );
    }
};
