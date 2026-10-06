#!/usr/bin/env python3
"""cram-lite: 极简 Cram 多米诺棋（Domineering 的无方向限制变体）。

规则：
- 8x8 棋盘，两名玩家轮流放一块 1x2 多米诺（横/竖皆可）。
- 无子可放者判负。

纯标准库：argparse / copy / random / sys。
"""

import argparse
import copy
import random
import sys

SIZE = 8  # 8x8 棋盘

# 走法：(r1, c1, r2, c2)，两格正交相邻


def new_board():
    """返回空棋盘：False=空格，True=被占。"""
    return [[False] * SIZE for _ in range(SIZE)]


def legal_moves(board):
    """枚举全部合法多米诺走法（横/竖）。"""
    moves = []
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c]:
                continue
            if c + 1 < SIZE and not board[r][c + 1]:
                moves.append((r, c, r, c + 1))  # 横
            if r + 1 < SIZE and not board[r + 1][c]:
                moves.append((r, c, r + 1, c))  # 竖
    return moves


def _check_move(board, move):
    (r1, c1, r2, c2) = move
    for r, c in ((r1, c1), (r2, c2)):
        if not (0 <= r < SIZE and 0 <= c < SIZE):
            raise ValueError(f"越界: {move}")
    if abs(r1 - r2) + abs(c1 - c2) != 1:
        raise ValueError(f"两格必须正交相邻: {move}")
    if board[r1][c1] or board[r2][c2]:
        raise ValueError(f"格子已被占: {move}")


def apply_move(board, move):
    """在棋盘上放一块多米诺。非法抛 ValueError，不修改原棋盘。"""
    _check_move(board, move)
    b = copy.deepcopy(board)
    (r1, c1, r2, c2) = move
    b[r1][c1] = True
    b[r2][c2] = True
    return b


def move_count_after(board, move):
    """走完 move 后对手的走法数（贪心评估用）。"""
    b = apply_move(board, move)
    return len(legal_moves(b))


def ai_move(board, rng):
    """贪心 AI：最小化对手后续走法数，平局按 seed 随机。"""
    moves = legal_moves(board)
    if not moves:
        return None
    scored = [(move_count_after(board, m), m) for m in moves]
    best = min(s for s, _ in scored)
    cands = [m for s, m in scored if s == best]
    return rng.choice(cands)


def render(board):
    lines = ["  " + " ".join(str(c) for c in range(SIZE))]
    for r in range(SIZE):
        lines.append(f"{r} " + " ".join("■" if board[r][c] else "·" for c in range(SIZE)))
    return "\n".join(lines)


def parse_coord(text):
    """解析 'r1 c1 r2 c2' 四个整数。"""
    parts = text.split()
    if len(parts) != 4:
        raise ValueError("请输入四个整数：r1 c1 r2 c2")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        raise ValueError("坐标必须是整数")


def play_interactive():
    if not sys.stdin.isatty():
        print("交互模式需要终端；无头演示请用 --auto", file=sys.stderr)
        sys.exit(2)
    board = new_board()
    turn = 0
    names = ["甲", "乙"]
    print("Cram 多米诺棋：轮流放 1x2 多米诺，无子可放者输。输入如 '0 0 0 1'，q 退出。")
    while True:
        print()
        print(render(board))
        moves = legal_moves(board)
        if not moves:
            print(f"{names[turn]} 无子可放，{names[1 - turn]} 获胜！")
            return
        print(f"{names[turn]} 走（{len(moves)} 种走法可选）：")
        try:
            line = input("> ").strip()
        except EOFError:
            print()
            return
        if line.lower() == "q":
            print("退出。")
            return
        try:
            move = parse_coord(line)
            board = apply_move(board, move)
        except ValueError as e:
            print(f"非法走法：{e}")
            continue
        turn = 1 - turn


def play_auto(games, seed, verbose):
    rng = random.Random(seed)
    w0 = w1 = 0
    for g in range(games):
        board = new_board()
        turn = 0
        n_moves = 0
        while True:
            move = ai_move(board, rng)
            if move is None:
                winner = 1 - turn
                if winner == 0:
                    w0 += 1
                else:
                    w1 += 1
                if verbose or games <= 10:
                    print(f"第 {g + 1}/{games} 局：{'甲' if winner == 0 else '乙'}胜（{n_moves} 手）")
                break
            board = apply_move(board, move)
            turn = 1 - turn
            n_moves += 1
    print(f"总计：甲胜 {w0}，乙胜 {w1}，和棋 0")
    return w0, w1


def main():
    ap = argparse.ArgumentParser(description="Cram 多米诺棋（8x8，无子可放者输）")
    ap.add_argument("--auto", action="store_true", help="AI 对 AI 自动演示")
    ap.add_argument("--games", type=int, default=10, help="自动演示局数")
    ap.add_argument("--seed", type=int, default=42, help="随机种子")
    ap.add_argument("--verbose", action="store_true", help="打印每局")
    args = ap.parse_args()
    if args.auto:
        play_auto(args.games, args.seed, args.verbose)
    else:
        play_interactive()


if __name__ == "__main__":
    main()
