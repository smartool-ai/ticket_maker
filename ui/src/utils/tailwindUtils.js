export const strCombine = (...args) => args.join(' ');

export const twConditional = (conditional, style) => (conditional ? style : '');

/**
 const tailwindClasses = {
    default: 'text-black',
    foo: 'bg-red',
    bar: 'border-black',
    baz: 'border-white',
  };
 EXAMPLE 1:
 const id = 'foo';
 twId(id, tailwindClasses) // 'text-black bg-red'
 EXAMPLE 2:
 const ids = ['foo', 'bar'];
 twId(ids, tailwindClasses) // 'text-black bg-red border-black'
 */

 export const twId = (ids, tailwindObject) => {
  if (ids && Array.isArray(ids)) {
    const tailwindIds = ids.map((id) => (id ? tailwindObject[id] : undefined)).join(' ');
    return [tailwindObject.default, tailwindIds].join(' ');
  }

  if (ids) {
    return [tailwindObject.default, tailwindObject[ids]].join(' ');
  }

  return tailwindObject.default;
};

/**
const tailwindClasses = {
    default: 'text-black',
    true: 'bg-green-500',
    false: 'bg-red-500',
  };
const conditional = true;
 twFilter(conditional, tailwindClasses) // 'text-black bg-green-500'
 */

export const twFilter = (conditional, tailwindObject) => [
  tailwindObject.default,
  tailwindObject[!!conditional],
].join(' ');