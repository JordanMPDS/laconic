const { S3Client, GetObjectCommand, PutObjectCommand } = require('@aws-sdk/client-s3');
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');

const s3 = new S3Client({ region: process.env.AWS_REGION });
const BUCKET = process.env.ASSET_BUCKET;

// Used today to hand buyers a time-limited link to an invoice PDF. The bucket
// policy denies public access; a signed URL is the only way in or out.
//
// The bucket accepts signed PUT as well - the same credentials, the same
// helper, method: 'PUT'. Nothing uses that yet. CORS on the bucket already
// allows PUT from market.example.com because it was configured from the
// same template as the internal tool.
exports.signedUrl = async (key, { method = 'GET', expiresIn = 900 } = {}) => {
  const Command = method === 'PUT' ? PutObjectCommand : GetObjectCommand;
  return getSignedUrl(s3, new Command({ Bucket: BUCKET, Key: key }), { expiresIn });
};
