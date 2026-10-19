[分割版目次](../README.md) | [前へ](appendix-b-rlp.md) | [次へ](appendix-d-trie.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="app:hexprefix"></span>

# 付録C. 16進接頭辞符号化

16進接頭辞符号化は、任意個数のニブルをバイト配列として符号化する効率的な方法である。追加のフラグを格納でき、この方式が用いられる唯一の文脈であるトライにおいて、ノード型の曖昧さを解消する。

これは、ニブル列（集合 $`\mathbb{Y}`$ で表す）とブール値を、バイト列（集合 $`\mathbb{B}`$ で表す）へ写す関数 $`\mathtt{HP}`$ として定義される。

<span id="eq-200"></span><span id="eq-201"></span>

```math
\begin{aligned}
\mathtt{HP}(\mathbf{x}, t): \mathbf{x} \in \mathbb{Y} & \equiv & \begin{cases}
(16f(t), 16\mathbf{x}[0] + \mathbf{x}[1], 16\mathbf{x}[2] + \mathbf{x}[3], ...) &
\text{if} \quad \lVert \mathbf{x} \rVert \; \text{is even} \\
(16(f(t) + 1) + \mathbf{x}[0], 16\mathbf{x}[1] + \mathbf{x}[2], 16\mathbf{x}[3] + \mathbf{x}[4], ...) &
\text{otherwise}
\end{cases} & \qquad \text{(200)} \\
f(t) & \equiv & \begin{cases} 2 & \text{if} \quad t \neq 0 \\ 0 & \text{otherwise} \end{cases} & \qquad \text{(201)}
\end{aligned}
```

したがって、先頭バイトの上位ニブルには二つのフラグが含まれる。最下位ビットは長さが奇数であることを符号化し、次のビットはフラグ $`t`$ を符号化する。先頭バイトの下位ニブルは、ニブル数が偶数の場合はゼロ、奇数の場合は最初のニブルとなる。残るニブルはすべて（この時点では偶数個）、残りのバイトへ適切に収まる。
