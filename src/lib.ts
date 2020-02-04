/**
 * Convert a sheet or field name into a form valid for use in named range. Will
 * change spaces to underscores and remove everything not a letter, number or
 * underscore.
 * 
 * For more on named range naming, see:
 * https://support.google.com/docs/answer/63175
 * 
 * @param name 
 */
export const slugify = (name: string): string => {
    return name.toLowerCase().replace(/\s/g, '_').replace(/\W/g, '')
}

/**
 * Converts a zero-based column index in a sheet into its corresponding alpha
 * notation. Column zero is A, column 1 is B, column 26 is AA, etc. Used when
 * selecting cells in a column via "A1 notation", e.g. "A1:A23".
 * 
 * For more on A1 notation, see:
 * https://developers.google.com/sheets/api/guides/concepts#a1_notation
 * 
 * @param index 
 */
export const indexToAlpha = (index: number): string => {
    const digits = index
        .toString(26) // convert to base-26 integer
        .split('') // split into individual digits
        .map(digit => parseInt(digit, 26)) // convert each digit back to base-10 to use as alpha offset

    if (digits.length > 1) digits[0] -= 1 // 0 -> 'A' so for multidigit numbers, adjust the most significant digit

    return digits
        .map(digit => String.fromCharCode(65 + digit)) // use the digit as an offset from 'A' (ASCII 65)
        .join('') // join resulting letters back together
}

// array.find polyfill, see:
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/find#Polyfill
// https://tc39.github.io/ecma262/#sec-array.prototype.find
if (!Array.prototype.find) {
    Object.defineProperty(Array.prototype, 'find', {
      value: function(predicate: any) {
        // 1. Let O be ? ToObject(this value).
        if (this == null) {
          throw TypeError('"this" is null or not defined');
        }
  
        var o = Object(this);
  
        // 2. Let len be ? ToLength(? Get(O, "length")).
        var len = o.length >>> 0;
  
        // 3. If IsCallable(predicate) is false, throw a TypeError exception.
        if (typeof predicate !== 'function') {
          throw TypeError('predicate must be a function');
        }
  
        // 4. If thisArg was supplied, let T be thisArg; else let T be undefined.
        var thisArg = arguments[1];
  
        // 5. Let k be 0.
        var k = 0;
  
        // 6. Repeat, while k < len
        while (k < len) {
          // a. Let Pk be ! ToString(k).
          // b. Let kValue be ? Get(O, Pk).
          // c. Let testResult be ToBoolean(? Call(predicate, T, « kValue, k, O »)).
          // d. If testResult is true, return kValue.
          var kValue = o[k];
          if (predicate.call(thisArg, kValue, k, o)) {
            return kValue;
          }
          // e. Increase k by 1.
          k++;
        }
  
        // 7. Return undefined.
        return undefined;
      },
      configurable: true,
      writable: true
    });
  }