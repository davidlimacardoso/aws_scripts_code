<div class="Prose_prose__7AjXb Prose_presets_prose__H9VRM Prose_presets_theme-hi-contrast__LQyM9 Prose_presets_preset-lg__5CAiC"><h1>AWS Lambda Function to Delete Old CloudWatch Logs</h1>
<h2>Overview</h2>
<p>This Lambda function is designed to identify and delete CloudWatch logs that are older than 5 years. It does this by listing log groups in an S3 bucket and sending messages to an SQS queue for processing.</p>
<h2>Prerequisites</h2>
<ul>
<li>AWS account with permissions to access S3 and SQS.</li>
<li>An S3 bucket named <code>ame-prd-log-groups-cloudwatch</code>.</li>
<li>An SQS queue named <code>ops-delete-cloudwatch-oldest-logs</code>.</li>
</ul>
<h2>Environment Variables</h2>
<ul>
<li><code>BUCKET</code>: The name of the S3 bucket containing the log groups.</li>
<li><code>REGION</code>: The AWS region where the resources are located (default is <code>us-east-1</code>).</li>
<li><code>ACCOUNT_ID</code>: Your AWS account ID.</li>
<li><code>SQS_QUEUE</code>: The name of the SQS queue used for processing.</li>
</ul>
<h2>Functionality</h2>
<ol>
<li><strong>List Prefixes</strong>: The function retrieves prefixes within the specified S3 bucket.</li>
<li><strong>Process Month</strong>: It checks each month path to determine if the logs are older than 5 years.</li>
<li><strong>Send Messages</strong>: Messages containing paths to old logs are sent to the SQS queue in batches.</li>
</ol>
<h2>Lambda Handler</h2>
<p>The entry point for the Lambda function is <code>lambda_handler</code>. It performs the following tasks:</p>
<ol>
<li><strong>Input Validation</strong>: Checks if a valid prefix is provided in the event.</li>
<li><strong>List Services</strong>: Retrieves services from the S3 bucket using the provided prefix.</li>
<li><strong>Concurrent Processing</strong>: Utilizes a thread pool to process each service concurrently.</li>
<li><strong>Send Messages to SQS</strong>: Sends messages for old log paths to the specified SQS queue.</li>
</ol>
<h3>Example Event</h3>
<div class="MarkdownCodeBlock_container__nRn2j"><div class="MarkdownCodeBlock_codeBlock__rvLec force-dark"><div class="MarkdownCodeBlock_codeHeader__zWt_V"><div class="MarkdownCodeBlock_languageName__4_BF8">json</div><div class="MarkdownCodeBlock_codeActions__wvgwQ"><button class="button_root__TL8nv button_ghost__YsMI5 button_sm__hWzjK button_center__RsQ_o button_showIconOnly-compact-below___fiXt MarkdownCodeBlock_codeActionButton__xJBAg" type="button" data-theme="ghost"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="m21.205 7.556-5.291-5.265A.995.995 0 0 0 15.209 2h-6.5a1 1 0 0 0-1 1v2.235h2V4h4.503v4.265a1 1 0 0 0 1 1H19.5v5.5h-1.209v2H20.5a1 1 0 0 0 1-1v-7.5a.998.998 0 0 0-.295-.709Zm-4.993-2.147 1.865 1.856h-1.865V5.409Z"></path><path d="m15.996 12.791-5.291-5.265a1 1 0 0 0-.705-.29H3.5a1 1 0 0 0-1 1V21a1 1 0 0 0 1 1h11.791a1 1 0 0 0 1-1v-7.5a1 1 0 0 0-.295-.709Zm-4.993-2.147 1.865 1.856h-1.865v-1.856ZM4.5 20V9.235h4.503V13.5a1 1 0 0 0 1 1h4.288V20H4.5Z"></path></svg><span class="button_label__mCaDf"></span></button></div></div><div class="" data-collapsed="unknown"><pre class="MarkdownCodeBlock_preTag__QMZEO MarkdownCodeBlock_horizontalOverflowHidden__YPHxg" style="display: block; overflow-x: auto; background: rgb(43, 43, 43); color: rgb(248, 248, 242); padding: 0.5em;"><code class="MarkdownCodeBlock_codeTag__5BV0Z" style="white-space: pre;"><span>{
</span><span>  </span><span class="hljs-attr">"prefix"</span><span>: </span><span style="color: rgb(171, 227, 56);">"aws/lambda/"</span><span>
</span>}
</code></pre></div></div></div>
<h2>Error Handling</h2>
<ul>
<li>Returns a 400 status code if the prefix is invalid.</li>
<li>Logs errors encountered during processing.</li>
</ul>
<h2>Usage</h2>
<p>Deploy this Lambda function in your AWS environment and trigger it with an appropriate event containing the prefix of the log groups you want to process.</p>
<h2>Dependencies</h2>
<ul>
<li><code>boto3</code>: AWS SDK for Python, used for interacting with S3 and SQS.</li>
<li><code>concurrent.futures</code>: For concurrent execution of tasks.</li>
</ul>
<h2>License</h2>
<p>This project is licensed under the MIT License.</p></div>
