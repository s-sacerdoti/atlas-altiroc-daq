if (( $# < 3 )); then
    echo 'Usage: bash gen_TOA_template.sh <template_file> <pixel_low> <pixel_high>'
    exit 1
fi

template_file=$1
pixel_low=$2
pixel_high=$3

if (( pixel_low == pixel_high )); then
    pixel_range=$pixel_low
    output_tag="${pixel_low}"
else
    pixel_range="${pixel_low}:$((pixel_high+1))"
    output_tag="${pixel_low}-${pixel_high}"
fi

output_file=$(echo $template_file | sed "s/template/${output_tag}/")

sed -e "s/TEMPLATE_PIXEL_RANGE/$pixel_range/" \
    -e "s/TEMPLATE_PIXEL_LOW/$pixel_low/" \
    -e "s/TEMPLATE_PIXEL_HIGH/$pixel_high/" $template_file > $output_file
