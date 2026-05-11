import { ROLE_REGISTRY as loginRegistry } from "../../login/user/role.js";
import {ROLE_REGISTRY as klausurRegistry} from "../../klausur/user/roles.js";
import { ROLE_REGISTRY as vorlesungenRegistry } from "../../vorlesungen/user/role.js";

const registries = {
    login: loginRegistry,
    klausur: klausurRegistry,
    vorlesungen: vorlesungenRegistry
};

export function loadRoleRegistry(testName) {

    const registry = registries[testName];

    if (!registry) {
        throw new Error(`Unknown registry: ${testName}`);
    }

    return registry;
}