[分割版目次](../README.md) | [前へ](appendix-d-trie.md) | [次へ](appendix-f-signing-transactions.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="app:precompiled"></span>

# 付録E. プリコンパイル済みコントラクト

各プリコンパイル済みコントラクトについて、gas不足検査を実装するテンプレート関数 $`\Xi_{\mathtt{PRE}}`$ を用いる。

<span id="eq-209"></span><span id="eq:pre"></span>

```math
\Xi_{\mathtt{PRE}}(\boldsymbol{\sigma}, g, A, I) \equiv \begin{cases}
(\varnothing, 0, A, ()) & \text{if} \quad g < g_{\mathrm{r}} \\
(\boldsymbol\sigma, g - g_{\mathrm{r}}, A, \mathbf{o}) & \text{otherwise}\end{cases} \qquad \text{(209)}
```

各プリコンパイル済みコントラクトはこれらの定義を用い、 $`\mathbf{o}`$ （出力データ）とgas要件 $`g_{\mathrm{r}}`$ の仕様を与える。

$`\Xi_{\mathtt{ECREC}}`$ を、楕円曲線デジタル署名アルゴリズム（ECDSA）の公開鍵復元関数（ecrecover）のプリコンパイル済みコントラクトとして定義する。関数 $`\mathtt{ECDSARECOVER}`$ と定数 $`\mathtt{secp256k1n}`$ の定義は[付録F](appendix-f-signing-transactions.md#app:signing)を参照されたい。また $`\mathbf{d}`$ を入力データとし、必要に応じてゼロを追加することで無限長に対して明確に定義する。署名が無効な場合、出力は返さない。

<span id="eq-210"></span><span id="eq-211"></span><span id="eq-212"></span><span id="eq-213"></span><span id="eq-214"></span><span id="eq-215"></span><span id="eq-216"></span><span id="eq-217"></span><span id="eq-218"></span><span id="eq-219"></span><span id="eq-220"></span><span id="eq-221"></span><span id="eq:ecrec_precompile_validity"></span>

```math
\begin{aligned}
\Xi_{\mathtt{ECREC}} &\equiv& \Xi_{\mathtt{PRE}} \quad \text{where:} & \qquad \text{(210)} \\
g_{\mathrm{r}} &=& 3000 & \qquad \text{(211)} \\
\lVert \mathbf{o} \rVert &=& \begin{cases}
  0 & \text{if} \quad v \notin \{27, 28\} \,\vee\, r = 0 \,\vee\, r \ge \mathtt{secp256k1n} \,\vee\, s = 0 \,\vee\, s \ge \mathtt{secp256k1n} \\
  0 & \text{if} \quad \mathtt{ECDSARECOVER}(h, v - 27, r, s) = \varnothing\\
  32 & \text{otherwise}
\end{cases} & \qquad \text{(212)} \\
\text{if} \quad \lVert \mathbf{o} \rVert = 32: && & \qquad \text{(213)} \\
\mathbf{o}[0..11] &=& 0 & \qquad \text{(214)} \\
\mathbf{o}[12..31] &=& \mathtt{KEC}\big(\mathtt{ECDSARECOVER}(h, v - 27, r, s)\big)[12..31] \quad \text{where:} & \qquad \text{(215)} \\
\mathbf{d}[0..(\lVert I_{\mathbf{d}} \rVert-1)] &=& I_{\mathbf{d}} & \qquad \text{(216)} \\
\mathbf{d}[\lVert I_{\mathbf{d}} \rVert..] &=& (0, 0, ...) & \qquad \text{(217)} \\
h &=& \mathbf{d}[0..31] & \qquad \text{(218)} \\
v &=& \mathbf{d}[32..63] & \qquad \text{(219)} \\
r &=& \mathbf{d}[64..95] & \qquad \text{(220)} \\
s &=& \mathbf{d}[96..127] & \qquad \text{(221)}
\end{aligned}
```

$`\Xi_{\mathtt{SHA256}}`$ と $`\Xi_{\mathtt{RIP160}}`$ を、それぞれSHA2-256およびRIPEMD-160ハッシュ関数を実装するプリコンパイル済みコントラクトとして定義する。そのgas使用量は、最も近いワード数へ切り上げた入力データ・サイズに依存する。

<span id="eq-222"></span><span id="eq-223"></span><span id="eq-224"></span><span id="eq-225"></span><span id="eq-226"></span><span id="eq-227"></span><span id="eq-228"></span>

```math
\begin{aligned}
\Xi_{\mathtt{SHA256}} &\equiv& \Xi_{\mathtt{PRE}} \quad \text{where:} & \qquad \text{(222)} \\
g_{\mathrm{r}} &=& 60 + 12\Big\lceil \dfrac{\lVert I_{\mathbf{d}} \rVert}{32} \Big\rceil & \qquad \text{(223)} \\
\mathbf{o}[0..31] &=& \mathtt{SHA256}(I_{\mathbf{d}}) & \qquad \text{(224)} \\
\Xi_{\mathtt{RIP160}} &\equiv& \Xi_{\mathtt{PRE}} \quad \text{where:} & \qquad \text{(225)} \\
g_{\mathrm{r}} &=& 600 + 120\Big\lceil \dfrac{\lVert I_{\mathbf{d}} \rVert}{32} \Big\rceil & \qquad \text{(226)} \\
\mathbf{o}[0..11] &=& 0 & \qquad \text{(227)} \\
\mathbf{o}[12..31] &=& \mathtt{RIPEMD160}(I_{\mathbf{d}}) & \qquad \text{(228)}
\end{aligned}
```

ここでは、次の形式を持つ、明確に定義されたRIPEMD-160およびSHA2-256の標準暗号関数が存在すると仮定する。

<span id="eq-229"></span><span id="eq-230"></span>

```math
\begin{aligned}
\mathtt{SHA256}(\mathbf{i} \in \mathbb{B}) & \equiv & o \in \mathbb{B}_{32} & \qquad \text{(229)} \\
\mathtt{RIPEMD160}(\mathbf{i} \in \mathbb{B}) & \equiv & o \in \mathbb{B}_{20} & \qquad \text{(230)}
\end{aligned}
```

第4のコントラクトである恒等関数 $`\Xi_{\mathtt{ID}}`$ は、出力を単に入力として定義する。

<span id="eq-231"></span><span id="eq-232"></span><span id="eq-233"></span>

```math
\begin{aligned}
\Xi_{\mathtt{ID}} &\equiv& \Xi_{\mathtt{PRE}} \quad \text{where:} & \qquad \text{(231)} \\
g_{\mathrm{r}} &=& 15 + 3\Big\lceil \dfrac{\lVert I_{\mathbf{d}} \rVert}{32} \Big\rceil & \qquad \text{(232)} \\
\mathbf{o} &=& I_{\mathbf{d}} & \qquad \text{(233)}
\end{aligned}
```

第5のコントラクトは、剰余下で任意精度の累乗を行う。ここで $`0 ^ 0`$ は1とし、すべての $`x`$ について $`x \bmod 0`$ はゼロとする。入力の第1ワードは第1の非負整数 $`B`$ が占めるバイト数を指定する。第2ワードは第2の非負整数 $`E`$ のバイト数を、第3ワードは第3の非負整数 $`M`$ のバイト数を指定する。これら三つのワードの後に $`B`$ 、 $`E`$ 、 $`M`$ が続く。入力の残りは破棄する。入力が短すぎる場合、不足するバイトはゼロとみなす。出力は $`M`$ と同じ形式へビッグエンディアンで符号化される。

<span id="eq-234"></span><span id="eq-235"></span><span id="eq-236"></span><span id="eq-237"></span><span id="eq-238"></span><span id="eq-239"></span><span id="eq-240"></span><span id="eq-241"></span><span id="eq-242"></span><span id="eq-243"></span><span id="eq-244"></span><span id="eq-245"></span><span id="eq-246"></span>

```math
\begin{aligned}
\Xi_{\mathtt{EXPMOD}} &\equiv& \Xi_{\mathtt{PRE}} \quad \text{except:} & \qquad \text{(234)} \\
g_{\mathrm{r}} &=& \max \left(200, \left\lfloor\frac{f\big(\max(\ell_{\mathrm{M}},\ell_{\mathrm{B}})\big)\max(\ell'_{\mathrm{E}},1)}{G_{\mathrm{quaddivisor}}}\right\rfloor \right) & \qquad \text{(235)} \\
G_{\mathrm{quaddivisor}} &\equiv& 3 & \qquad \text{(236)} \\
f(x) &\equiv& \left\lceil \frac{x}{8} \right\rceil ^2 & \qquad \text{(237)} \\
\ell'_{\mathrm{E}} &=& \begin{cases}
0 & \text{if}\ \ell_{\mathrm{E}}\le 32\wedge E=0 \\
\lfloor \log_2(E)\rfloor &\text{if}\ \ell_{\mathrm{E}}\le 32 \wedge E \neq 0 \\
8(\ell_{\mathrm{E}} - 32) + \lfloor \log_2(i[(96+\ell_{\mathrm{B}})..(127+\ell_{\mathrm{B}})]) \rfloor & \text{if}\ 32 < \ell_{\mathrm{E}} \wedge i[(96 + \ell_{\mathrm{B}})..(127 + \ell_{\mathrm{B}})]\neq 0 \\
8(\ell_{\mathrm{E}} - 32) & \text{otherwise} \\
\end{cases} & \qquad \text{(238)} \\
\mathbf{o} &=& \left(B^E\bmod M\right)\in\mathbb{N}_{8\ell_{\mathrm{M}}} & \qquad \text{(239)} \\
\ell_{\mathrm{B}} &\equiv& i[0..31] & \qquad \text{(240)} \\
\ell_{\mathrm{E}} &\equiv& i[32..63] & \qquad \text{(241)} \\
\ell_{\mathrm{M}} &\equiv& i[64..95] & \qquad \text{(242)} \\
B &\equiv& i[96..(95+\ell_{\mathrm{B}})] & \qquad \text{(243)} \\
E &\equiv& i[(96+\ell_{\mathrm{B}})..(95+\ell_{\mathrm{B}}+\ell_{\mathrm{E}})] & \qquad \text{(244)} \\
M &\equiv& i[(96+\ell_{\mathrm{B}}+\ell_{\mathrm{E}})..(95+\ell_{\mathrm{B}}+\ell_{\mathrm{E}}+\ell_{\mathrm{M}})] & \qquad \text{(245)} \\
i[x] &\equiv& \begin{cases}
I_{\mathbf{d}}[x] &\text{if}\ x < \lVert I_{\mathbf{d}} \rVert \\
0 &\text{otherwise}
\end{cases} & \qquad \text{(246)}
\end{aligned}
```

## E.1. zkSNARK 関連プリコンパイル済みコントラクト

いずれも素数である二つの数を選ぶ。

<span id="eq-247"></span><span id="eq-248"></span>

```math
\begin{aligned}
p &\equiv& 21888242871839275222246405745257275088696311157297823662689037894645226208583 & \qquad \text{(247)} \\
q &\equiv& 21888242871839275222246405745257275088548364400416034343698204186575808495617 & \qquad \text{(248)}
\end{aligned}
```

$`p`$ は素数であるため、 $`\{0, 1, \ldots, p - 1\}`$ は $`p`$ を法とする加算および乗算について体をなす。この体を $`F_{\mathrm{p}}`$ と呼ぶ。

集合 $`C_1`$ を次のように定義する。

<span id="eq-249"></span>

```math
C_1\equiv\{(X,Y)\in F_{\mathrm{p}}\times F_{\mathrm{p}}\mid Y^2=X^3+3\}\cup\{(0,0)\} \qquad \text{(249)}
```

相異なる要素 $`(X_1, Y_1), (X_2, Y_2)`$ について、 $`C_1`$ 上の二項演算 $`+`$ を次のように定義する。

<span id="eq-250"></span><span id="eq:ec-addition"></span>

```math
\begin{aligned}
(X_1, Y_1) + (X_2, Y_2)&\equiv&\begin{cases}
(X,Y)&\text{if}\ X_1\neq X_2\\
(0,0)&\text{otherwise}
\end{cases} & \qquad \text{(250)} \\
\lambda&\equiv&\frac{Y_2-Y_1}{X_2-X_1} \\
X&\equiv&\lambda^2-X_1-X_2 \\
Y&\equiv&\lambda(X_1-X)-Y_1
\end{aligned}
```

$`(X_1, Y_1) = (X_2, Y_2)`$ の場合、 $`C_1`$ 上の $`+`$ を次のように定義する。

<span id="eq-251"></span><span id="eq:ec-doubling"></span>

```math
\begin{aligned}
(X_1, Y_1) + (X_2, Y_2)&\equiv&\begin{cases}
(X,Y)&\text{if}\ Y_1\neq 0\\
(0,0)&\text{otherwise}
\end{cases} & \qquad \text{(251)} \\
\lambda&\equiv&\frac{3X_1^2}{2Y_1} \\
X&\equiv&\lambda^2-2X_1 \\
Y&\equiv&\lambda(X_1-X)-Y_1
\end{aligned}
```

<span id="tnref-6"></span>[訳注6](../translation-notes.md#tn-6)

$`(C_1,+)`$ は群をなすことが知られている。自然数 $`n`$ と $`C_1`$ 上の点 $`P`$ に対し、スカラー乗算 $`\cdot`$ を次のように定義する。

<span id="eq-252"></span><span id="eq:ec-scalar-multiplication"></span>

```math
n\cdot P\equiv(0,0)+\underbrace{P+\cdots+P}_{n} \qquad \text{(252)}
```

$`P_1`$ を $`C_1`$ 上の点 $`(1,2)`$ と定義する。 $`G_1`$ を $`P_1`$ が生成する $`(C_1,+)`$ の部分群とする。 $`G_1`$ は位数 $`q`$ の巡回群であることが知られている。 $`G_1`$ 内の点 $`P`$ について、 $`\log_{P_1}(P)`$ を $`n\cdot P_1=P`$ を満たす最小の自然数 $`n`$ と定義する。 $`\log_{P_1}(P)`$ は高々 $`q-1`$ である。

$`F_{p^2}`$ を体 $`F_{p}[i]/(i^2+1)`$ とする。集合 $`C_2`$ を次のように定義する。

<span id="eq-253"></span>

```math
C_2\equiv\{(X,Y)\in F_{p^2}\times F_{p^2}\mid Y^2=X^3+3(i+9)^{-1}\}\cup\{(0,0)\} \qquad \text{(253)}
```

二項演算 $`+`$ およびスカラー乗算 $`\cdot`$ を、式（[250](#eq:ec-addition)）、（[251](#eq:ec-doubling)）、（[252](#eq:ec-scalar-multiplication)）と同じ式によって定義する。 $`(C_2,+)`$ も群であることが知られている。 $`C_2`$ 内の $`P_2`$ を次のように定義する。

<span id="eq-254"></span>

```math
\begin{aligned}
P_2&\equiv&
(11559732032986387107991004021392285783925812861821192530917403151452391805634 \times i & \qquad \text{(254)} \\
&&+ 10857046999023057135944570762232829481370756359578518086990519993285655852781, \\
&& 4082367875863433681332203403145435568316851327593401208105741076214120093531 \times i \\
&&+ 8495653923123431417604973247489272438418190587263600148770280649306958101930)
\end{aligned}
```

$`G_2`$ を $`P_2`$ が生成する $`(C_2,+)`$ の部分群と定義する。 $`G_2`$ は、 $`C_2`$ 上で位数 $`q`$ を持つ唯一の巡回群であることが知られている。 $`G_2`$ 内の点 $`P`$ について、 $`\log_{P_2}(P)`$ を $`n\cdot P_2=P`$ を満たす最小の自然数 $`n`$ と定義する。この定義により、 $`\log_{P_2}(P)`$ は高々 $`q-1`$ である。

$`G_T`$ を $`F_{q^{12}}`$ の基礎となる乗法的アーベル群とする。非退化双線形写像 $`e : G_1\times G_2 \to G_T`$ が存在することが知られている。この双線形写像はタイプ3ペアリングである。このような双線形写像は複数存在するが、そのどれを $`e`$ として選んでも構わない。 $`P_T = e(P_1, P_2)`$ とし、 $`a`$ を $`G_1`$ 内の $`k`$ 個の点の集合、 $`b`$ を $`G_2`$ 内の $`k`$ 個の点の集合とする。ペアリングの定義から、次の二つは同値である。

<span id="eq-255"></span><span id="eq-256"></span><span id="eq:pairing-check"></span>

```math
\begin{aligned}
\log_{P_1}(a_1)\times\log_{P_2}(b_1)+\cdots+\log_{P_1}(a_{k})\times\log_{P_2}(b_{k})&\equiv& 1\mod q & \qquad \text{(255)} \\
\prod_{i=0}^{k}e\left(a_i, b_i\right) &=& P_T & \qquad \text{(256)}
\end{aligned}
```

したがって、ペアリング演算は式（[255](#eq:pairing-check)）を検証する方法を提供する。

<span id="tnref-7"></span>[訳注7](../translation-notes.md#tn-7)

<span id="tnref-8"></span>[訳注8](../translation-notes.md#tn-8)

32バイトの数 $`\mathbf{x}\in\mathbf{P}_{256}`$ は、 $`F_{\mathrm{p}}`$ の要素を表す場合と表さない場合がある。

<span id="eq-257"></span>

```math
\delta_{\mathrm{p}}(\mathbf{x})\equiv\begin{cases}
\mathbf{x}&\text{if}\ \mathbf{x}<p\\
\varnothing&\text{otherwise}
\end{cases} \qquad \text{(257)}
```

64バイトのデータ $`\mathbf{x}\in\mathbf{B}_{512}`$ は、 $`G_1`$ の要素を表す場合と表さない場合がある。

<span id="eq-258"></span><span id="eq-259"></span><span id="eq-260"></span><span id="eq-261"></span>

```math
\begin{aligned}
\delta_1(\mathbf{x})&\equiv&\begin{cases}
g_1&\text{if}\ g_1\in G_1\\
\varnothing&\text{otherwise}
\end{cases} & \qquad \text{(258)} \\
g_1&\equiv&\begin{cases}
(x,y)&\text{if}\ x\neq\varnothing\wedge y\neq\varnothing\\
\varnothing&\text{otherwise}
\end{cases} & \qquad \text{(259)} \\
x&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[0..31]) & \qquad \text{(260)} \\
y&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[32..63]) & \qquad \text{(261)}
\end{aligned}
```

128バイトのデータ $`\mathbf{x}\in\mathbf{B}_{1024}`$ は、 $`G_2`$ の要素を表す場合と表さない場合がある。

<span id="eq-262"></span><span id="eq-263"></span><span id="eq-264"></span><span id="eq-265"></span><span id="eq-266"></span><span id="eq-267"></span>

```math
\begin{aligned}
\delta_2(\mathbf{x})&\equiv&\begin{cases}
g_2&\text{if}\ g_2\in G_2\\
\varnothing&\text{otherwise}
\end{cases} & \qquad \text{(262)} \\
g_2&\equiv&\begin{cases}
((x_0i+y_0),(x_1i+y_1))&\text{if}\ x_0\neq\varnothing\wedge y_0\neq\varnothing\wedge x_1\neq\varnothing\wedge y_1\neq\varnothing\\
\varnothing&\text{otherwise}
\end{cases} & \qquad \text{(263)} \\
x_0&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[0..31]) & \qquad \text{(264)} \\
y_0&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[32..63]) & \qquad \text{(265)} \\
x_1&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[64..95]) & \qquad \text{(266)} \\
y_1&\equiv&\delta_{\mathrm{p}}(\mathbf{x}[96..127]) & \qquad \text{(267)}
\end{aligned}
```

$`\Xi_{\mathtt{SNARKV}}`$ を、zkSNARK検証での使用を意図し、式（[255](#eq:pairing-check)）が成り立つかを検査するプリコンパイル済みコントラクトとして定義する。

<span id="eq-268"></span><span id="eq-269"></span><span id="eq-270"></span><span id="eq-271"></span><span id="eq-272"></span><span id="eq-273"></span><span id="eq-274"></span><span id="eq-275"></span><span id="eq-276"></span><span id="eq-277"></span><span id="eq-278"></span>

```math
\begin{aligned}
\Xi_{\mathtt{SNARKV}}&\equiv&\Xi_{\mathtt{PRE}}\quad\text{except:} & \qquad \text{(268)} \\
\qquad\Xi_{\mathtt{SNARKV}}(\boldsymbol\sigma,g,A,I)&=&\left(\varnothing,0,A,()\right)\quad\text{if}\ F & \qquad \text{(269)} \\
F&\equiv&(\lVert I_{\mathbf{d}} \rVert\bmod 192\neq 0\vee(\exists j.\ a_{\mathrm{j}}=\varnothing\vee b_{\mathrm{j}}=\varnothing)) & \qquad \text{(270)} \\
k &=& \dfrac{\lVert I_{\mathbf{d}} \rVert}{192} & \qquad \text{(271)} \\
g_{\mathrm{r}}&=& 34000k + 45000 & \qquad \text{(272)} \\
\mathbf{o}[0..31]&\equiv&\begin{cases}
0x0000000000000000000000000000000000000000000000000000000000000001&\text{if}\ v\wedge\neg F\\
0x0000000000000000000000000000000000000000000000000000000000000000&\text{if}\ \neg v\wedge\neg F
\end{cases} & \qquad \text{(273)} \\
v&\equiv&(\log_{P_1}(a_1)\times\log_{P_2}(b_1)+\cdots+\log_{P_1}(a_k)\times\log_{P_2}(b_k)\equiv 1\mod q) & \qquad \text{(274)} \\
a_1&\equiv&\delta_1(I_{\mathbf{d}}[0..63]) & \qquad \text{(275)} \\
b_1&\equiv&\delta_2(I_{\mathbf{d}}[64..191]) & \qquad \text{(276)} \\
\vdots \\
a_k&\equiv&\delta_1(I_{\mathbf{d}}[(\lVert I_{\mathbf{d}} \rVert-192)..(\lVert I_{\mathbf{d}} \rVert-129)]) & \qquad \text{(277)} \\
b_k&\equiv&\delta_2(I_{\mathbf{d}}[(\lVert I_{\mathbf{d}} \rVert-128)..(\lVert I_{\mathbf{d}} \rVert-1)]) & \qquad \text{(278)}
\end{aligned}
```

$`G_1`$ 上の加算を行うプリコンパイル済みコントラクトを定義する。

<span id="eq-279"></span><span id="eq-280"></span><span id="eq-281"></span><span id="eq-282"></span><span id="eq-283"></span><span id="eq-284"></span><span id="eq-285"></span><span id="eq:complemented_input"></span>

```math
\begin{aligned}
\Xi_{\mathtt{BN\_ADD}}&\equiv&\Xi_{\mathtt{BN\_PRE}}\quad\text{except:} & \qquad \text{(279)} \\
\Xi_{\mathtt{BN\_ADD}}(\boldsymbol\sigma,g,A,I)&=&\left(\varnothing,0,A,()\right)\quad\text{if}\ x=\varnothing\vee y=\varnothing & \qquad \text{(280)} \\
g_{\mathrm{r}} &=& 150 & \qquad \text{(281)} \\
\mathbf{o}&\equiv&\delta_1^{-1}(x+y)\quad\text{ここで }+\text{ は }G_1\text{ の群演算} & \qquad \text{(282)} \\
x&\equiv&\delta_1\left(\bar I_{\mathbf{d}}[0..63]\right) & \qquad \text{(283)} \\
y&\equiv&\delta_1\left(\bar I_{\mathbf{d}}[64..127]\right) & \qquad \text{(284)} \\
\bar I_{\mathbf{d}}[x]&\equiv&\begin{cases}
I_{\mathbf{d}}[x]&\text{if}\ x < \lVert I_{\mathbf{d}} \rVert\\
0&\text{otherwise}
\end{cases} & \qquad \text{(285)}
\end{aligned}
```

<span id="tnref-9"></span>[訳注9](../translation-notes.md#tn-9)

$`G_1`$ 上のスカラー乗算を行うプリコンパイル済みコントラクトを定義する。ここで $`\bar I_{\mathbf{d}}`$ は式（[285](#eq:complemented_input)）で定義される。

<span id="eq-286"></span><span id="eq-287"></span><span id="eq-288"></span><span id="eq-289"></span><span id="eq-290"></span><span id="eq-291"></span>

```math
\begin{aligned}
\Xi_{\mathtt{BN\_MUL}}&\equiv&\Xi_{\mathtt{PRE}}\quad\text{except:} & \qquad \text{(286)} \\
\Xi_{\mathtt{BN\_MUL}}(\boldsymbol\sigma,g,A,I)&=&\left(\varnothing,0,A,()\right)\quad\text{if}\ x=\varnothing & \qquad \text{(287)} \\
g_{\mathrm{r}} &=& 6000 & \qquad \text{(288)} \\
\mathbf{o}&\equiv&\delta_1^{-1}(n\cdot x)\quad\text{ここで }\cdot\text{ は }G_1\text{ のスカラー乗算} & \qquad \text{(289)} \\
x&\equiv&\delta_1\left(\bar I_{\mathbf{d}}[0..63]\right) & \qquad \text{(290)} \\
n&\equiv&\bar I_{\mathbf{d}}[64..95] & \qquad \text{(291)}
\end{aligned}
```

## E.2. BLAKE2 プリコンパイル済みコントラクト

[(Hess et al. 2016)](../references.md#ref-EIP-152) によるEIP-152は、BLAKE2暗号学的ハッシュ・アルゴリズムで用いる圧縮関数 $`\mathtt{F}`$ を実装するプリコンパイル済みコントラクトとして $`\Xi_{\mathtt{BLAKE2\_F}}`$ を定義する。圧縮関数 $`\mathtt{F}`$ は、[(Saarinen and Aumasson 2015)](../references.md#ref-RFC-7693) によるRFC 7693で規定されている。

<span id="eq-292"></span><span id="eq-293"></span><span id="eq-294"></span><span id="eq-295"></span><span id="eq-296"></span><span id="eq-297"></span><span id="eq-298"></span><span id="eq-299"></span><span id="eq-300"></span><span id="eq-301"></span><span id="eq-302"></span><span id="eq-303"></span><span id="eq-304"></span><span id="eq-305"></span><span id="eq-306"></span>

```math
\begin{aligned}
\Xi_{\mathtt{BLAKE2\_F}}&\equiv&\Xi_{\mathtt{PRE}}\quad\text{except:} & \qquad \text{(292)} \\
\Xi_{\mathtt{BLAKE2\_F}}(\boldsymbol\sigma,g,A,I)&=&\left(\varnothing,0,A,()\right)\quad\text{if}\ \lVert I_{\mathbf{d}}\rVert \neq 213 \vee f \notin \{0, 1\} & \qquad \text{(293)} \\
g_{\mathrm{r}} &=& r & \qquad \text{(294)} \\
\mathbf{o} &\equiv& \mathtt{LE}_8(h'_0)\cdot ... \cdot \mathtt{LE}_8(h'_7) & \qquad \text{(295)} \\
(h'_0,\dots,h'_7) &\equiv& \mathtt{F}(h, m, t_\mathrm{low}, t_\mathrm{high}, f) \quad(r\text{ ラウンド、}w = 64) & \qquad \text{(296)} \\
\mathtt{BE}_4(r) &\equiv& I_{\mathbf{d}}[0..4] & \qquad \text{(297)} \\
\mathtt{LE}_8(h_0) &\equiv& I_{\mathbf{d}}[4..12] & \qquad \text{(298)} \\
&\dots& & \qquad \text{(299)} \\
\mathtt{LE}_8(h_7) &\equiv& I_{\mathbf{d}}[60..68] & \qquad \text{(300)} \\
\mathtt{LE}_8(m_0) &\equiv& I_{\mathbf{d}}[68..76] & \qquad \text{(301)} \\
&\dots& & \qquad \text{(302)} \\
\mathtt{LE}_8(m_{15}) &\equiv& I_{\mathbf{d}}[188..196] & \qquad \text{(303)} \\
\mathtt{LE}_8(t_\mathrm{low}) &\equiv& I_{\mathbf{d}}[196..204] & \qquad \text{(304)} \\
\mathtt{LE}_8(t_\mathrm{high}) &\equiv& I_{\mathbf{d}}[204..212] & \qquad \text{(305)} \\
f &\equiv& I_{\mathbf{d}}[212] & \qquad \text{(306)}
\end{aligned}
```

ここで $`r \in \mathbb{B}_{32}`$ 、 $`\forall i \in 0..7: h_i \in \mathbb{B}_{64}`$ 、 $`\forall i \in 0..15: m_i \in \mathbb{B}_{64}`$ 、 $`t_\mathrm{low} \in \mathbb{B}_{64}`$ 、 $`t_\mathrm{high} \in \mathbb{B}_{64}`$ 、 $`f \in \mathbb{B}_8`$ である。 $`\mathtt{BE}_k`$ は $`k`$ バイトのビッグエンディアン表現である（[195](appendix-b-rlp.md#eq:BE)と比較されたい）。

<span id="tnref-10"></span>[訳注10](../translation-notes.md#tn-10)

<span id="eq-307"></span>

```math
\mathtt{BE}_k(x) \equiv (b_0, b_1, ..., b_{k-1}): x = \sum_{n = 0}^{k-1} b_n \cdot 256^{k-1-n} \qquad \text{(307)}
```

また、 $`\mathtt{LE}_k`$ は $`k`$ バイトのリトルエンディアン表現である。

<span id="eq-308"></span>

```math
\mathtt{LE}_k(x) \equiv (b_0, b_1, ..., b_{k-1}): x = \sum_{n = 0}^{k-1} b_n \cdot 256^n \qquad \text{(308)}
```
