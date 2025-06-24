<div class="Message_messageTextContainer__w64Sc"><div class="Message_selectableText__SQ8WH"><div class="Markdown_markdownContainer__Tz3HQ"><div class="Prose_prose__7AjXb Prose_presets_prose__H9VRM Prose_presets_theme-hi-contrast__LQyM9 Prose_presets_preset-lg__5CAiC"><h1>AWS Lambda Function to Delete S3 Objects</h1>
<h2>Overview</h2>
<p>This AWS Lambda function is designed to process messages from an SQS queue and delete specified prefixes in an S3 bucket. It facilitates the automatic cleanup of unwanted S3 objects based on messages received.</p>
<h2>Prerequisites</h2>
<ul>
<li>An AWS account with permissions to access S3 and SQS.</li>
<li>An S3 bucket named <code>ame-prd-log-groups-cloudwatch</code>.</li>
<li>An SQS queue named <code>ops-delete-cloudwatch-oldest-logs</code>.</li>
</ul>
<h2>Environment Variables</h2>
<ul>
<li><code>BUCKET</code>: The name of the S3 bucket from which objects will be deleted.</li>
<li><code>REGION</code>: The AWS region where the resources are located (default is <code>us-east-1</code>).</li>
<li><code>ACCOUNT_ID</code>: Your AWS account ID.</li>
<li><code>SQS_QUEUE</code>: The name of the SQS queue used for processing.</li>
</ul>
<h2>Functionality</h2>
<ol>
<li><strong>Delete S3 Prefix</strong>: Deletes all objects under a specified prefix in the S3 bucket.</li>
<li><strong>Process SQS Queue</strong>: Continuously polls the SQS queue for messages, processes each message, and deletes corresponding S3 prefixes.</li>
<li><strong>Error Handling</strong>: Logs any errors encountered during message processing.</li>
</ol>
<h2>Lambda Handler</h2>
<p>The entry point for the Lambda function is <code>lambda_handler</code>. It calls the <code>process_queue</code> function, which handles the following tasks:</p>
<ol>
<li><strong>Receive Messages</strong>: Fetches messages from the SQS queue.</li>
<li><strong>Process Each Message</strong>: For each message, it parses the JSON body and extracts the S3 prefix.</li>
<li><strong>Delete S3 Objects</strong>: Calls the <code>delete_s3_prefix</code> function to delete objects under the specified prefix.</li>
<li><strong>Delete Message from Queue</strong>: Removes the message from the queue after processing.</li>
</ol>
<h3>Example Message Format</h3>
<p>The message sent to the SQS queue should look like this:</p>
<div class="MarkdownCodeBlock_container__nRn2j"><div class="MarkdownCodeBlock_codeBlock__rvLec force-dark"><div class="MarkdownCodeBlock_codeHeader__zWt_V"><div class="MarkdownCodeBlock_languageName__4_BF8">json</div><div class="MarkdownCodeBlock_codeActions__wvgwQ"><button class="button_root__TL8nv button_ghost__YsMI5 button_sm__hWzjK button_center__RsQ_o button_showIconOnly-compact-below___fiXt MarkdownCodeBlock_codeActionButton__xJBAg" type="button" data-theme="ghost"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="m21.205 7.556-5.291-5.265A.995.995 0 0 0 15.209 2h-6.5a1 1 0 0 0-1 1v2.235h2V4h4.503v4.265a1 1 0 0 0 1 1H19.5v5.5h-1.209v2H20.5a1 1 0 0 0 1-1v-7.5a.998.998 0 0 0-.295-.709Zm-4.993-2.147 1.865 1.856h-1.865V5.409Z"></path><path d="m15.996 12.791-5.291-5.265a1 1 0 0 0-.705-.29H3.5a1 1 0 0 0-1 1V21a1 1 0 0 0 1 1h11.791a1 1 0 0 0 1-1v-7.5a1 1 0 0 0-.295-.709Zm-4.993-2.147 1.865 1.856h-1.865v-1.856ZM4.5 20V9.235h4.503V13.5a1 1 0 0 0 1 1h4.288V20H4.5Z"></path></svg><span class="button_label__mCaDf"></span></button></div></div><div class="" data-collapsed="unknown"><pre class="MarkdownCodeBlock_preTag__QMZEO MarkdownCodeBlock_horizontalOverflowHidden__YPHxg" style="display: block; overflow-x: auto; background: rgb(43, 43, 43); color: rgb(248, 248, 242); padding: 0.5em;"><code class="MarkdownCodeBlock_codeTag__5BV0Z" style="white-space: pre;"><span>{
</span><span>  </span><span class="hljs-attr">"path"</span><span>: </span><span style="color: rgb(171, 227, 56);">"your/s3/prefix/"</span><span>
</span>}
</code></pre></div></div></div>
<h2>Usage</h2>
<ol>
<li>Deploy this Lambda function in your AWS environment.</li>
<li>Configure the necessary permissions for S3 and SQS.</li>
<li>Send messages to the SQS queue containing the S3 prefixes you want to delete.</li>
</ol>
<h2>Dependencies</h2>
<ul>
<li><code>boto3</code>: AWS SDK for Python, used for interacting with S3 and SQS.</li>
</ul>
<h2>License</h2>
<p>This project is licensed under the MIT License.</p></div></div></div></div>
