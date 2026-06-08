import { sleep} from 'k6';
export function randomBetween(min, max) {
    return Math.random() * (max - min) + min;
}

export function think(thinkTime) {
    sleep(randomBetween(thinkTime[0], thinkTime[1]));
}

