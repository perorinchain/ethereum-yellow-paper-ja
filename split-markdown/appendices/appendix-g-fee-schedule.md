[分割版目次](../README.md) | [前へ](appendix-f-signing-transactions.md) | [次へ](appendix-h-virtual-machine.md) | [単一ページ版](../../ethereum_yellow_paper_ja.md)

<span id="app:fees"></span>

# 付録G. 手数料表

手数料表 $`G`$ は、トランザクションが引き起こし得る複数の抽象演算について、gas単位の相対コストに対応するスカラー値のタプルである。

| 名前 | 値 | 説明 |
| --- | --- | --- |
| $`G_{\mathrm{zero}}`$ | 0 | 集合 $`W_{\mathrm{zero}}`$ の演算には支払わない。 |
| $`G_{\mathrm{jumpdest}}`$ | 1 | JUMPDEST演算に支払うgas量。 |
| $`G_{\mathrm{base}}`$ | 2 | 集合 $`W_{\mathrm{base}}`$ の演算に支払うgas量。 |
| $`G_{\mathrm{verylow}}`$ | 3 | 集合 $`W_{\mathrm{verylow}}`$ の演算に支払うgas量。 |
| $`G_{\mathrm{low}}`$ | 5 | 集合 $`W_{\mathrm{low}}`$ の演算に支払うgas量。 |
| $`G_{\mathrm{mid}}`$ | 8 | 集合 $`W_{\mathrm{mid}}`$ の演算に支払うgas量。 |
| $`G_{\mathrm{high}}`$ | 10 | 集合 $`W_{\mathrm{high}}`$ の演算に支払うgas量。 |
| $`G_{\mathrm{warmaccess}}`$ | 100 | ウォームなアカウントまたはストレージへのアクセス・コスト。 |
| $`G_{\mathrm{accesslistaddress}}`$ | 2400 | アクセス・リストによってアカウントをウォームにするコスト。 |
| $`G_{\mathrm{accessliststorage}}`$ | 1900 | アクセス・リストによってストレージをウォームにするコスト。 |
| $`G_{\mathrm{coldaccountaccess}}`$ | 2600 | コールドなアカウントへのアクセス・コスト。 |
| $`G_{\mathrm{coldsload}}`$ | 2100 | コールドなストレージへのアクセス・コスト。 |
| $`G_{\mathrm{sset}}`$ | 20000 | SSTORE演算によってストレージ値をゼロから非ゼロへ設定するときに支払う。 |
| $`G_{\mathrm{sreset}}`$ | 2900 | SSTORE演算によってストレージ値のゼロ／非ゼロの別が変わらないとき、または ゼロに設定するときに支払う。 |
| $`R_{\mathrm{sclear}}`$ | 4800 | ストレージ値を非ゼロからゼロへ設定するときに与える還付（還付カウンタへ加算）。 還付額は $`G_{\mathrm{sreset}} + G_{\mathrm{accessliststorage}}`$ と定義される。 |
| $`G_{\mathrm{selfdestruct}}`$ | 5000 | SELFDESTRUCT演算に支払うgas量。 |
| $`G_{\mathrm{create}}`$ | 32000 | CREATE演算に支払う。 |
| $`G_{\mathrm{codedeposit}}`$ | 200 | CREATE演算がコードを状態へ正常に配置する際に、1バイトごとに支払う。 |
| $`G_{\mathrm{initcodeword}}`$ | 2 | デプロイ・トランザクション、CREATE演算、またはCREATE2演算の開始時に、 初期化コード1ワードごとに支払う。 |
| $`G_{\mathrm{callvalue}}`$ | 9000 | CALL演算の一部として非ゼロ値を移転するときに支払う。 |
| $`G_{\mathrm{callstipend}}`$ | 2300 | 非ゼロ値の移転について $`G_{\mathrm{callvalue}}`$ から差し引き、呼出先コントラクトへ与える給付gas。 |
| $`G_{\mathrm{newaccount}}`$ | 25000 | アカウントを作成するCALLまたはSELFDESTRUCT演算に支払う。 |
| $`G_{\mathrm{exp}}`$ | 10 | EXP演算に対する部分的な支払い。 |
| $`G_{\mathrm{expbyte}}`$ | 50 | EXP演算について、指数のバイト数を乗じる部分的な支払い。 |
| $`G_{\mathrm{memory}}`$ | 3 | メモリ拡張時、追加する1ワードごとに支払う。 |
| $`G_\text{txcreate}`$ | 32000 | *Homestead* 移行後、コントラクトを作成するすべてのトランザクションが支払う。 |
| $`G_{\mathrm{txdatazero}}`$ | 4 | トランザクションのデータまたはコードに含まれるゼロ・バイトごとに支払う。 |
| $`G_{\mathrm{txdatanonzero}}`$ | 16 | トランザクションのデータまたはコードに含まれる非ゼロ・バイトごとに支払う。 |
| $`G_{\mathrm{transaction}}`$ | 21000 | トランザクションごとに支払う。 |
| $`G_{\mathrm{log}}`$ | 375 | LOG演算に対する部分的な支払い。 |
| $`G_{\mathrm{logdata}}`$ | 8 | LOG演算のデータ1バイトごとに支払う。 |
| $`G_{\mathrm{logtopic}}`$ | 375 | LOG演算のトピックごとに支払う。 |
| $`G_{\mathrm{keccak256}}`$ | 30 | KECCAK256演算ごとに支払う。 |
| $`G_{\mathrm{keccak256word}}`$ | 6 | KECCAK256演算の入力データについて、切り上げたワードごとに支払う。 |
| $`G_{\mathrm{copy}}`$ | 3 | \*COPY演算に対する部分的な支払いであり、コピーするワード数を切り上げた値を乗じる。 |
| $`G_{\mathrm{blockhash}}`$ | 20 | BLOCKHASH演算ごとの支払い。 |
