export function render(template, vars) {

    return template.replace(/\{\{(.*?)\}\}/g, (_, key) => {
        return vars[key.trim()];
    });
}