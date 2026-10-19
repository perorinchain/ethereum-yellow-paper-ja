[分割版目次](../README.md) | [前へ](07-contract-creation.md) | [次へ](09-execution-model.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="ch:call"></span>

# 8. メッセージ呼び出し

メッセージ呼び出しの実行には、送信者 $`s`$ 、トランザクション起点者 $`o`$ 、受信者 $`r`$ 、コードを実行するアカウント $`c`$ （通常は受信者と同じ）、利用可能 gas $`g`$ 、値 $`v`$ 、実効 gas 価格 $`p`$ 、呼び出しの入力データである任意長バイト配列 $`\mathbf{d}`$ 、現在のメッセージ呼び出し／コントラクト作成スタック深度 $`e`$ 、最後に状態変更の許可 $`w`$ が必要である。

メッセージ呼び出しには、新しい状態と累積トランザクション・サブ状態への評価に加えて、バイト配列 $`\mathbf{o}`$ で表す出力データという追加の構成要素がある。これはトランザクション実行時には無視されるが、メッセージ呼び出しはVMコードの実行によって開始される場合があり、その場合にはこの情報を用いる。

<span id="eq-119"></span>

```math
(\boldsymbol{\sigma}', g', A', z, \mathbf{o}) \equiv {\Theta}(\boldsymbol{\sigma}, A, s, o, r, c, g, p, v, \tilde{v}, \mathbf{d}, e, w) \qquad \text{(119)}
```

DELEGATECALL命令では、移転する値 $`v`$ と、実行文脈から見える値 $`\tilde{v}`$ とを区別する必要があることに注意されたい。

最初の遷移状態 $`\boldsymbol{\sigma}_1`$ を、送信者から受信者へ値を移転した元の状態として定義する。

<span id="eq-120"></span>

```math
\boldsymbol{\sigma}_1[r]_{\mathrm{b}} \equiv \boldsymbol{\sigma}[r]_{\mathrm{b}} + v \quad\wedge\quad \boldsymbol{\sigma}_1[s]_{\mathrm{b}} \equiv \boldsymbol{\sigma}[s]_{\mathrm{b}} - v \qquad \text{(120)}
```

ただし $`s = r`$ の場合を除く。

本稿全体を通じて、 $`\boldsymbol{\sigma}_1[r]`$ が元々未定義であった場合、コードも状態もなく、残高とnonceがゼロのアカウントとして作成されると仮定する。したがって、直前の式は次の意味に解するべきである。

<span id="eq-121"></span>

```math
\boldsymbol{\sigma}_1 \equiv \boldsymbol{\sigma}_1' \quad \text{except:} \qquad \text{(121)}
```

<span id="eq-122"></span>

```math
\boldsymbol{\sigma}_1[s] \equiv \begin{cases}
\varnothing & \text{if}\ \boldsymbol{\sigma}_1'[s] = \varnothing \ \wedge\ v = 0 \\
\mathbf{a}_1 &\text{otherwise}
\end{cases} \qquad \text{(122)}
```

<span id="eq-123"></span>

```math
\mathbf{a}_1 \equiv \left(\boldsymbol{\sigma}_1'[s]_{\mathrm{n}}, \boldsymbol{\sigma}_1'[s]_{\mathrm{b}} - v, \boldsymbol{\sigma}_1'[s]_{\mathbf{s}}, \boldsymbol{\sigma}_1'[s]_{\mathrm{c}}\right) \qquad \text{(123)}
```

<span id="eq-124"></span>

```math
\text{and}\quad \boldsymbol{\sigma}_1' \equiv \boldsymbol{\sigma} \quad \text{except:} \qquad \text{(124)}
```

<span id="eq-125"></span>

```math
\begin{cases}
\boldsymbol{\sigma}_1'[r] \equiv (0, v, \mathtt{TRIE}(\varnothing), \mathtt{KEC}(())) & \text{if} \quad \boldsymbol{\sigma}[r] = \varnothing \wedge v \neq 0 \\
\boldsymbol{\sigma}_1'[r] \equiv \varnothing & \text{if}\quad \boldsymbol{\sigma}[r] = \varnothing \wedge v = 0 \\
\boldsymbol{\sigma}_1'[r] \equiv \mathbf{a}_1' & \text{otherwise}
\end{cases} \qquad \text{(125)}
```

<span id="eq-126"></span>

```math
\mathbf{a}_1' \equiv (\boldsymbol{\sigma}[r]_{\mathrm{n}}, \boldsymbol{\sigma}[r]_{\mathrm{b}} + v, \boldsymbol{\sigma}[r]_{\mathbf{s}}, \boldsymbol{\sigma}[r]_{\mathrm{c}}) \qquad \text{(126)}
```

アカウントの関連コード（Keccak-256 ハッシュが $`\boldsymbol{\sigma}[c]_{\mathrm{c}}`$ となる断片）は、実行モデル（[第9節](09-execution-model.md#ch:model)参照）に従って実行する。コントラクト作成と同様、実行が例外的に停止した場合（gas の枯渇、スタック・アンダーフロー、無効なジャンプ先、無効な命令など）、呼び出し元に gas を払い戻さず、状態を残高移転直前、すなわち $`\boldsymbol{\sigma}`$ へ戻す。

<span id="eq-127"></span><span id="eq-128"></span><span id="eq-129"></span><span id="eq-130"></span><span id="eq-131"></span><span id="eq-132"></span><span id="eq-133"></span><span id="eq-134"></span><span id="eq-135"></span><span id="eq-136"></span><span id="eq-137"></span><span id="eq-138"></span><span id="eq-139"></span><span id="code_execution_result"></span>

```math
\begin{aligned}
\boldsymbol{\sigma}' & \equiv & \begin{cases}
\boldsymbol{\sigma} & \text{if} \quad \boldsymbol{\sigma}^{**} = \varnothing \\
\boldsymbol{\sigma}^{**} & \text{otherwise}
\end{cases} & \qquad \text{(127)} \\
g' & \equiv & \begin{cases}
0 & \text{if} \quad \boldsymbol{\sigma}^{**} = \varnothing \ \wedge \\
&\quad \mathbf{o} = \varnothing \\
g^{**} & \text{otherwise}
\end{cases} & \qquad \text{(128)} \\
A' & \equiv & \begin{cases}
A & \text{if} \quad \boldsymbol{\sigma}^{**} = \varnothing \\
A^{**} & \text{otherwise}
\end{cases} & \qquad \text{(129)} \\
z & \equiv & \begin{cases}
0 & \text{if} \quad \boldsymbol{\sigma}^{**} = \varnothing \\
1 & \text{otherwise}
\end{cases} & \qquad \text{(130)} \\
(\boldsymbol{\sigma}^{**}, g^{**}, A^{**}, \mathbf{o}) & \equiv & \Xi & \qquad \text{(131)} \\
I_{\mathrm{a}} & \equiv & r & \qquad \text{(132)} \\
I_{\mathrm{o}} & \equiv & o & \qquad \text{(133)} \\
I_{\mathrm{p}} & \equiv & p & \qquad \text{(134)} \\
I_{\mathbf{d}} & \equiv & \mathbf{d} & \qquad \text{(135)} \\
I_{\mathrm{s}} & \equiv & s & \qquad \text{(136)} \\
I_{\mathrm{v}} & \equiv & \tilde{v} & \qquad \text{(137)} \\
I_{\mathrm{e}} & \equiv & e & \qquad \text{(138)} \\
I_{\mathrm{w}} & \equiv & w & \qquad \text{(139)}
\end{aligned}
```

ここで、

<span id="eq-140"></span>

```math
\Xi \equiv \begin{cases}
\Xi_{\mathtt{ECREC}}    (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 1 \\
\Xi_{\mathtt{SHA256}}   (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 2 \\
\Xi_{\mathtt{RIP160}}   (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 3 \\
\Xi_{\mathtt{ID}}       (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 4 \\
\Xi_{\mathtt{EXPMOD}}   (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 5 \\
\Xi_{\mathtt{BN\_ADD}}  (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 6 \\
\Xi_{\mathtt{BN\_MUL}}  (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 7 \\
\Xi_{\mathtt{SNARKV}}   (\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 8 \\
\Xi_{\mathtt{BLAKE2\_F}}(\boldsymbol{\sigma}_1, g, A, I) & \text{if} \quad c = 9 \\
\Xi                     (\boldsymbol{\sigma}_1, g, A, I) & \text{otherwise} \end{cases} \qquad \text{(140)}
```

かつ

<span id="eq-141"></span>

```math
\mathtt{KEC}(I_{\mathbf{b}}) = \boldsymbol{\sigma}[c]_{\mathrm{c}} \qquad \text{(141)}
```

とする。 $`I_{\mathbf{b}}`$ を決定可能にするため、クライアントはそれ以前のある時点でペア $`(\mathtt{KEC}(I_{\mathbf{b}}), I_{\mathbf{b}})`$ を格納済みであると仮定する。

見て分かるように、メッセージ呼び出しを評価する際の一般実行フレームワーク $`\Xi`$ の使用には九つの例外がある。これらはいわゆる「プリコンパイル済み」コントラクトであり、後に*ネイティブ拡張*となり得る予備的なアーキテクチャとして意図されている。アドレス1から9のコントラクトは、それぞれ楕円曲線公開鍵復元関数、SHA2 256ビット・ハッシュ方式、RIPEMD 160ビット・ハッシュ方式、恒等関数、任意精度モジュラー累乗、楕円曲線加算、楕円曲線スカラー乗算、楕円曲線ペアリング検査、BLAKE2圧縮関数 $`\mathtt{F}`$ を実行する。完全な形式的定義は[付録E](../appendices/appendix-e-precompiled-contracts.md#app:precompiled)にある。<span id="precompiled_set"></span>プリコンパイル済みコントラクトのアドレス集合を $`\pi`$ と表す。

<span id="eq-142"></span>

```math
\pi \equiv \{1, 2, 3, 4, 5, 6, 7, 8, 9 \} \qquad \text{(142)}
```
