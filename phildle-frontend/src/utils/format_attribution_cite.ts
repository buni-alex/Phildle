export function formatImageAttribution(meta: Record<string, any> | null): string {
  if (!meta) return "";

  const parts: string[] = [];

  // helper to remove unwanted block tags
  const flattenHTML = (html: string) =>
    html.replace(/<\/?(p|ul|li)[^>]*>/g, '').trim();

  // Wikipedia link
  if (meta.description_url) {
    parts.push(`<a href="${meta.description_url}" target="_blank">Wikipedia</a>`);
  } else {
    parts.push("Wikipedia");
  }

  if (meta.author) {
    const authorText = flattenHTML(meta.author);
    if (meta.author_url) {
      parts.push(`by <a href="${meta.author_url}" target="_blank">${authorText}</a>`);
    } else {
      parts.push(`by ${authorText}`);
    }
  }

  if (meta.credit) {
    const creditText = flattenHTML(meta.credit);
    if (meta.credit_url) {
      parts.push(`(${creditText}: <a href="${meta.credit_url}" target="_blank">${meta.credit_url}</a>)`);
    } else {
      parts.push(`(${creditText})`);
    }
  }

  if (meta.license) {
    const licenseText = flattenHTML(meta.license);
    if (meta.license_url) {
      parts.push(`[${licenseText}] <a href="${meta.license_url}" target="_blank">license</a>`);
    } else {
      parts.push(licenseText);
    }
  }

  return `<div style="font-size: 0.7em; color: #666; margin-top: 0.25em; line-height: 1.1; text-align: justify;">Image: ${parts.join(" ")}</div>`;
}