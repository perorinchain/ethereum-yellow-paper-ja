[分割版目次](README.md) | [前へ](appendices/appendix-l-mathematical-symbols.md) | [単一ページ版](../ethereum_yellow_paper_ja.md)

<div id="translator-notes" class="translator-notes" role="doc-endnotes">

# 訳注（日本語訳で追加）

以下は翻訳時に加えた補足・疑義であり、原文の本文・付録・脚注には含まれない。原文の脚注番号1〜12とは独立した番号を用いる。

<div id="tn-1" class="translator-note" role="doc-endnote">

**訳注1（原文を保存）。** 第4.2節の定義では **init** を「サイズ無制限」としているが、[トランザクション実行の妥当性条件](chapters/06-transaction-execution.md#ch:transactions)では、コントラクト作成トランザクションの initcode を49152バイト以下に制限している。ここでは原文の記述を保存した。

[参照箇所へ戻る](chapters/04-blocks-state-transactions.md#tnref-1)

</div>

<div id="tn-2" class="translator-note" role="doc-endnote">

**訳注2（原文を保存）。** 第4.3節の引き出しの直列化式の最後の成分は、原文では $`T_{\mathrm{a}}`$ となっている。同節の **amount** の定義からは $`W_{\mathrm{a}}`$ と考えられるが、ここでは原文の記号を保存した。

[参照箇所へ戻る](chapters/04-blocks-state-transactions.md#tnref-2)

</div>

<div id="tn-3" class="translator-note" role="doc-endnote">

**訳注3（原文を保存・補足）。** 第4.4.4節の基本手数料増加時の式は増分 $`\nu`$ を最低1とするため、基本手数料が1 Weiから2 Weiへ増える場合など、増加率が12.5%を超えることもある。同節にある増加率の説明は原文のまま保存した。

[参照箇所へ戻る](chapters/04-blocks-state-transactions.md#tnref-3)

</div>

<div id="tn-4" class="translator-note" role="doc-endnote">

**訳注4（原文を保存・補足）。** 第9.1節で、原文はメモリを「word-addressed byte array」と表現している。ただし、[命令一覧](appendices/appendix-h-virtual-machine.md#subsec:instruction-set)のMLOAD、MSTORE、MSTORE8の定義では、メモリの位置はバイト単位で指定される。32バイトのワードを読み書きする命令でも、指定位置が32の倍数である必要はない。

[参照箇所へ戻る](chapters/09-execution-model.md#tnref-4)

</div>

<div id="tn-5" class="translator-note" role="doc-endnote">

**訳注5（原文を保存）。** 第10.1節では、原文の予定時刻「2023-04-12 10:27:35 UTC」をそのまま記した。Ethereum Foundationの[当時の公式告知](https://blog.ethereum.org/2023/03/28/shapella-mainnet-announcement)では、同じエポック194,048の予定時刻は「2023-04-12 22:27:35 UTC」とされており、原文の時刻には誤記がある。

[参照箇所へ戻る](chapters/10-proof-of-stake-transition.md#tnref-5)

</div>

<div id="tn-6" class="translator-note" role="doc-endnote">

**訳注6（原文を保存・未解決の疑義）。** 付録E.1の楕円曲線の加算式には、無限遠点を表す $`(0,0)`$ を加法単位元として扱う規則が明記されていない。たとえば、相異なる点の式をそのまま $`(0,0)+(1,2)`$ に適用すると $`(3,-6)`$ となり、これは曲線の方程式を満たさない。無限遠点の符号化については [EIP-196](https://eips.ethereum.org/EIPS/eip-196#encoding) を参照されたい。

[参照箇所へ戻る](appendices/appendix-e-precompiled-contracts.md#tnref-6)

</div>

<div id="tn-7" class="translator-note" role="doc-endnote">

**訳注7（原文を保存・未解決の疑義）。** 付録E.1のペアリングの積は添字0から始まるが、同じ箇所に定義された点列は添字1から始まる。また、原文の検査条件は離散対数の積の和が $`1\bmod q`$ となることであり、同付録の $`\Xi_{\mathtt{SNARKV}}`$ も同じ条件を使う。一方、[EIP-197](https://eips.ethereum.org/EIPS/eip-197#specification) のプリコンパイルが検査するのは、この和が $`0\bmod q`$ 、すなわちペアリングの積が乗法単位元1となる条件である。本訳では原文の式を変更していない。

[参照箇所へ戻る](appendices/appendix-e-precompiled-contracts.md#tnref-7)

</div>

<div id="tn-8" class="translator-note" role="doc-endnote">

**訳注8（原文を保存・未解決の疑義）。** 付録E.1では、原文は $`G_T`$ を $`F_{q^{12}}`$ の乗法群としている。しかし、この群の位数 $`q^{12}-1`$ は $`q`$ の倍数ではないため、位数 $`q`$ の群からの非退化ペアリングについての同付録の説明とは整合しない。ここでも原文の $`q`$ を保存している。

[参照箇所へ戻る](appendices/appendix-e-precompiled-contracts.md#tnref-8)

</div>

<div id="tn-9" class="translator-note" role="doc-endnote">

**訳注9（原文を保存・未解決の疑義）。** 付録E.1の $`\Xi_{\mathtt{BN\_ADD}}`$ の定義に現れる $`\Xi_{\mathtt{BN\_PRE}}`$ は原文中で定義されていない。他のプリコンパイル済みコントラクトで使うテンプレートは $`\Xi_{\mathtt{PRE}}`$ である。

[参照箇所へ戻る](appendices/appendix-e-precompiled-contracts.md#tnref-9)

</div>

<div id="tn-10" class="translator-note" role="doc-endnote">

**訳注10（原文を保存・未解決の疑義）。** 付録E.2の範囲表記は、両端を含める本稿の一般的な規約と整合しない。たとえば $`I_{\mathbf{d}}[0..4]`$ はその規約では5バイトだが、 $`\mathtt{BE}_4(r)`$ は4バイトである。また、 $`\mathbb{B}_k`$ は本稿では $`k`$ バイトの列を表すのに対し、同付録の型の添字32・64・8はビット数に対応している。[EIP-152](https://eips.ethereum.org/EIPS/eip-152#specification) では $`r`$ は4バイト、各 $`h_i`$ ・ $`m_i`$ ・カウンタは8バイト、 $`f`$ は1バイトであり、全入力は213バイトとなる。

[参照箇所へ戻る](appendices/appendix-e-precompiled-contracts.md#tnref-10)

</div>

<div id="tn-11" class="translator-note" role="doc-endnote">

**訳注11（原文を保存・未解決の疑義）。** 付録H.2のCALLCODEとDELEGATECALLの説明中の引数番号は原文どおりである。ただし、第8節で定義する $`\Theta(\boldsymbol{\sigma}, A, s, o, r, c, g, p, v, \tilde v, \mathbf{d}, e, w)`$ では、宛先 $`r`$ は第5引数、送信者 $`s`$ は第3引数、実行文脈上の値 $`\tilde v`$ は第10引数であり、説明にある第4・第2・第9引数という番号と一致しない。

[参照箇所へ戻る](appendices/appendix-h-virtual-machine.md#tnref-11)

</div>

<div id="tn-12" class="translator-note" role="doc-endnote">

**訳注12（原文を保存・未解決の疑義）。** 付録J.3の説明はサイズの素数性を要求するが、原文の $`E_{\mathrm{prime}}`$ は $`x/y`$ が自然数かどうかだけを判定しており、素数判定を含まない。たとえば初期データセット・サイズを求める引数では $`x/y=2^{23}-1`$ は自然数なので、そのまま $`x`$ が返される。しかし、この商は $`47\times178481`$ と分解できる。

[参照箇所へ戻る](appendices/appendix-j-ethash.md#tnref-12)

</div>

<div id="tn-13" class="translator-note" role="doc-endnote">

**訳注13（原文を保存・未解決の疑義）。** 付録J.4.1の説明文は最初のエポックのシードを「32バイトのゼロ列のKeccak-256ハッシュ」としているが、同小節の式はハッシュを取らず $`\mathbf{0}_{32}`$ 自体を返す。説明と式の相違をそのまま保存した。

[参照箇所へ戻る](appendices/appendix-j-ethash.md#tnref-13)

</div>

<div id="tn-14" class="translator-note" role="doc-endnote">

**訳注14（原文を保存・未解決の疑義）。** 付録J.5のバイト順反転式では、原文の添字を保存した。0始まりの添字規約では、 $`i=0`$ の右辺は配列の範囲外となる。バイト順反転の添字なら通常は $`\lVert\mathbf{n}\rVert-1-i`$ となる。

[参照箇所へ戻る](appendices/appendix-j-ethash.md#tnref-14)

</div>

<div id="tn-15" class="translator-note" role="doc-endnote">

**訳注15（原文を保存・未解決の疑義）。** 付録J.5の原文では $`E_{\mathrm{accesses}}`$ の左辺は4引数であるのに対し、再帰呼び出しは3引数であり、データセット $`\mathbf{d}`$ の引数が欠けている。式は原文のままとした。

[参照箇所へ戻る](appendices/appendix-j-ethash.md#tnref-15)

</div>

<div id="tn-16" class="translator-note" role="doc-endnote">

**訳注16（原文を保存・未解決の疑義）。** 付録Lの数学記号一覧の説明の第2文は原文どおりだが、最小上界は元の要素の集合に属するとは限らず、一般にはその集合の最大要素ではない。たとえば包含関係で順序付けた集合族では、 $`\{1\}`$ と $`\{2\}`$ の結びは $`\{1,2\}`$ であり、元の二要素のいずれでもない。

[参照箇所へ戻る](appendices/appendix-l-mathematical-symbols.md#tnref-16)

</div>

</div>
