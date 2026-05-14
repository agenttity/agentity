import { sha256 } from '@noble/hashes/sha256';

const ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

export function base58Encode(buf: Uint8Array): string {
  let n = BigInt('0x' + Array.from(buf).map(b => b.toString(16).padStart(2, '0')).join(''));
  if (n === 0n) return ALPHABET[0];
  let result = '';
  while (n > 0n) {
    result = ALPHABET[Number(n % 58n)] + result;
    n /= 58n;
  }
  return result;
}

export { sha256 };
