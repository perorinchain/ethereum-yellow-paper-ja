[分割版目次](../README.md) | [前へ](appendix-c-hex-prefix.md) | [次へ](appendix-e-precompiled-contracts.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="app:trie"></span>

# 付録D. 修正 Merkle Patricia 木

<div id="trie">

</div>

修正Merkle Patricia木（トライ）は、任意長のバイナリ・データ（バイト配列）間を対応付ける永続データ構造を提供する。これは、256ビットのバイナリ断片と任意長のバイナリ・データを対応付ける可変データ構造によって定義され、通常はデータベースとして実装される。トライの中核であり、プロトコル仕様上の唯一の要件は、与えられたキー／値ペア集合を識別する単一の値を提供することである。その値は32バイト列または空バイト列のいずれかとなる。プロトコルを有効かつ効率的に実現できるようトライ構造を格納・維持する方法は、実装上の考慮事項に委ねられる。

形式的には、一意なキーを持つバイト列のペアを含む集合である入力値 $`\mathfrak{I}`$ を仮定する。

<span id="eq-202"></span>

```math
\mathfrak{I} = \{ (\mathbf{k}_0 \in \mathbb{B}, \mathbf{v}_0 \in \mathbb{B}), (\mathbf{k}_1 \in \mathbb{B}, \mathbf{v}_1 \in \mathbb{B}), ... \} \qquad \text{(202)}
```

このような列を考える際、タプルのキーまたは値を参照するため、一般的な数値添字記法を用いる。

<span id="eq-203"></span>

```math
\forall I \in \mathfrak{I}: I \equiv (I_0, I_1) \qquad \text{(203)}
```

任意のバイト列は、エンディアンを指定する記法があれば自明にニブル列ともみなせる。ここではビッグエンディアンを仮定する。したがって、

<span id="eq-204"></span><span id="eq-205"></span>

```math
\begin{aligned}
y(\mathfrak{I}) & = & \{ (\mathbf{k}_0' \in \mathbb{Y}, \mathbf{v}_0 \in \mathbb{B}), (\mathbf{k}_1' \in \mathbb{Y}, \mathbf{v}_1 \in \mathbb{B}), ... \} & \qquad \text{(204)} \\
\forall n: \quad \forall i < 2\lVert\mathbf{k}_{n}\rVert: \quad \mathbf{k}_{n}'[i] & \equiv &
\begin{cases}
\lfloor \mathbf{k}_{n}[i \div 2] \div 16 \rfloor & \text{if} \; i \; \text{is even} \\
\mathbf{k}_{n}[\lfloor i \div 2 \rfloor] \bmod 16 & \text{otherwise}
\end{cases} & \qquad \text{(205)}
\end{aligned}
```

この構造で符号化したときに当該集合を表すトライのルートへ評価される関数 $`\texttt{TRIE}`$ を定義する。

<span id="eq-206"></span>

```math
\texttt{TRIE}(\mathfrak{I}) \equiv \texttt{KEC}\big(\texttt{RLP} (c(\mathfrak{I}, 0))\big) \qquad \text{(206)}
```

さらに、トライのノード・キャップ関数 $`n`$ を仮定する。ノードを構成するとき、RLPを用いて構造を符号化する。ストレージの複雑さを減らすため、構成後のRLPが32バイト未満のノードは直接格納し、それ以外のノードについては、そのKeccak-256ハッシュが参照値へ評価されるバイト配列が既知であるとする。したがって、ノード構成関数 $`c`$ によって次のように定義する。

<span id="eq-207"></span>

```math
n(\mathfrak{I}, i) \equiv \begin{cases}
() \in \mathbb{B} & \text{if} \quad \mathfrak{I} = \varnothing \\
c(\mathfrak{I}, i) & \text{if} \quad \lVert \, \texttt{RLP} \big( c(\mathfrak{I}, i) \big) \rVert < 32 \\
\texttt{KEC}\big(\texttt{RLP}( c(\mathfrak{I}, i)) \big) & \text{otherwise}
\end{cases} \qquad \text{(207)}
```

基数木と同様に、トライをルートから葉まで走査すると単一のキー／値ペアを構築できる。走査中、各分岐ノードから一つのニブルを取得してキーを累積する（基数木と同様である）。基数木と異なり、複数のキーが同じ接頭辞を共有する場合、または単一のキーが一意な接尾辞を持つ場合には、二種類の最適化ノードが提供される。したがって走査中、残る二つのノード型である拡張ノードと葉ノードからは、複数のニブルを取得する可能性がある。トライには三種類のノードがある。

Leaf
: 二要素の構造であり、第1要素は、ルートから走査したキーと分岐の累積によってまだ処理されていないキー内のニブルに対応する。16進接頭辞符号化方式を用い、関数の第2引数は1でなければならない。

Extension
: 二要素の構造であり、第1要素は、ルートからの走査でニブルと分岐のキーを累積した部分より先にある、少なくとも二つの異なるキーに共有される長さ1超のニブル列に対応する。16進接頭辞符号化方式を用い、関数の第2引数は0でなければならない。

Branch
: 17項目からなる構造であり、最初の16項目は、キーの走査におけるこの地点で取り得る16通りのニブル値のそれぞれに対応する。17番目の項目は、これが終端ノードであり、したがってキーの走査がこの地点で終了する場合に用いられる。

したがって分岐は必要な場合にのみ用いられ、非ゼロ項目を一つしか含まない分岐ノードは存在してはならない。この構造を、構造構成関数 $`c`$ によって形式的に定義できる。

<span id="eq-208"></span>

```math
c(\mathfrak{I}, i) \equiv \begin{cases}
 \big(\texttt{HP}(I_0[i .. (\lVert I_0\rVert - 1)], 1), I_1 \big) & \text{if} \quad \lVert \mathfrak{I} \rVert = 1 \quad \text{where} \; \exists I: I \in \mathfrak{I} \\
\big(\texttt{HP}(I_0[i .. (j - 1)], 0), n(\mathfrak{I}, j) \big) & \text{if} \quad i \ne j \quad \text{where} \; j = \max \{ x : \exists \mathbf{l}: \lVert \mathbf{l} \rVert = x \wedge \forall I \in \mathfrak{I}: I_0[0 .. (x - 1)] = \mathbf{l} \} \\
(u(0), u(1), ..., u(15), v) & \text{otherwise} \quad \text{where} \begin{array}{rcl}
u(j) & \equiv & n(\{ I : I \in \mathfrak{I} \wedge I_0[i] = j \}, i + 1) \\
v & = & \begin{cases}
I_1 & \text{if} \quad \exists I: I \in \mathfrak{I} \wedge \lVert I_0 \rVert = i \\
() \in \mathbb{B} & \text{otherwise}
\end{cases}
\end{array}
\end{cases} \qquad \text{(208)}
```

## D.1. トライ・データベース

したがって、どのデータを格納し何を格納しないかは実装固有の考慮事項であるため、明示的な仮定を置かない。キー／値集合 $`\mathfrak{I}`$ を32バイト・ハッシュへ写す識別関数を定義し、任意の $`\mathfrak{I}`$ についてそのようなハッシュが一つだけ存在すると規定するだけである。これは厳密には真ではないものの、Keccakハッシュの衝突耐性を考えれば許容可能な精度で正しい。実際には、適切な実装が各集合についてトライのルート・ハッシュを完全に再計算することはない。

適切な実装は、さまざまなトライの計算から得られたノードのデータベースを維持する。より形式的には関数 $`c`$ をメモ化する。この戦略はトライの性質を利用して、以前の任意のキー／値集合の内容を容易に復元するとともに、複数の集合を非常に効率よく格納する。依存関係により、所与のルート・ハッシュを持つトライ内に特定の葉が必ず存在することを示すMerkle証明を、 $`O(\log N)`$ の空間要件で構成できる。
